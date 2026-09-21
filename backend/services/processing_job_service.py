"""Durable processing-job state for ingestion pipeline stages."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from backend.document_processing.pipeline.context import ProcessingContext
from backend.models.enums import PipelineStage, ProcessingJobStatus
from backend.models.processing_job import ProcessingJob
from backend.repositories.processing_job_repository import ProcessingJobRepository

if TYPE_CHECKING:
    from backend.services.pipeline_event_service import PipelineEventService


class ProcessingJobService:
    """Track durable current state for ingestion processing stages.

    ``ProcessingJob`` stores the latest durable state of each stage. Pipeline
    events are emitted alongside those state transitions through the optional
    ``PipelineEventService`` dependency. The event service uses its own
    database session and is intentionally non-blocking for ingestion.
    """

    _STAGE_SEQUENCE: dict[PipelineStage, int] = {
        PipelineStage.VALIDATION: 1,
        PipelineStage.EXTRACTION: 2,
        PipelineStage.CHUNKING: 3,
        PipelineStage.EMBEDDING: 4,
        PipelineStage.INDEXING: 5,
    }

    # CHUNKING completion is intentionally deferred until the persistence
    # layer commits the chunk checkpoint. This prevents the processing job
    # from claiming a durable checkpoint before the underlying artifacts are
    # actually committed.
    _DEFERRED_COMPLETION_STAGES = {PipelineStage.CHUNKING}

    _STAGE_ALIASES: dict[str, PipelineStage] = {
        "Validation": PipelineStage.VALIDATION,
        "Parsing": PipelineStage.EXTRACTION,
        "Chunking": PipelineStage.CHUNKING,
    }

    def __init__(
        self,
        repository: ProcessingJobRepository,
        event_service: PipelineEventService | None = None,
    ) -> None:
        self._repository = repository
        self._event_service = event_service
        self._active: dict[PipelineStage, tuple[ProcessingJob, datetime]] = {}

    # ------------------------------------------------------------------
    # Public stage API
    # ------------------------------------------------------------------

    def start_stage(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
    ) -> ProcessingJob:
        """Create or restart the durable job for a stage."""

        if stage not in self._STAGE_SEQUENCE:
            raise ValueError(
                f"Pipeline stage '{stage.value}' is not an executable processing stage."
            )

        existing = self._repository.get_by_ingestion_and_stage(
            ingestion_id=ingestion_id,
            stage=stage,
        )

        is_retry = existing is not None and existing.status in {
            ProcessingJobStatus.FAILED,
            ProcessingJobStatus.CANCELLED,
        }

        if existing is None:
            job = self._repository.create_running(
                ingestion_id=ingestion_id,
                stage=stage,
                sequence_number=self._STAGE_SEQUENCE[stage],
            )
        elif existing.status == ProcessingJobStatus.COMPLETED:
            raise ValueError(
                f"Processing stage '{stage.value}' is already completed for "
                f"ingestion '{ingestion_id}'."
            )
        else:
            job = self._repository.mark_running(existing)

        self._active[stage] = (job, datetime.now(timezone.utc))

        if is_retry:
            self._record_retry_requested(
                ingestion_id=ingestion_id,
                stage=stage,
                retry_count=job.retry_count,
            )

        self._record_started(
            ingestion_id=ingestion_id,
            stage=stage,
            retry_count=job.retry_count,
        )

        return job

    def complete_stage(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        records_processed: int = 0,
    ) -> ProcessingJob:
        """Persist successful completion of a stage and emit an event."""

        job, started_at = self._get_active_job(
            ingestion_id=ingestion_id,
            stage=stage,
        )
        duration_ms = int(
            (datetime.now(timezone.utc) - started_at).total_seconds() * 1000
        )
        completed = self._repository.mark_completed(
            job,
            duration_ms=duration_ms,
            records_processed=records_processed,
        )
        self._active.pop(stage, None)

        self._record_completed(
            ingestion_id=ingestion_id,
            stage=stage,
            duration_ms=completed.duration_ms or 0,
            records_processed=completed.records_processed,
            retry_count=completed.retry_count,
        )

        return completed

    def fail_stage(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        exception: Exception,
    ) -> ProcessingJob:
        """Persist failure of a stage and emit an event."""

        job, started_at = self._get_active_job(
            ingestion_id=ingestion_id,
            stage=stage,
        )
        duration_ms = int(
            (datetime.now(timezone.utc) - started_at).total_seconds() * 1000
        )
        failed = self._repository.mark_failed(
            job,
            duration_ms=duration_ms,
            exception=exception,
        )
        self._active.pop(stage, None)

        self._record_failed(
            ingestion_id=ingestion_id,
            stage=stage,
            duration_ms=failed.duration_ms or 0,
            exception=exception,
            retry_count=failed.retry_count,
        )

        return failed

    # ------------------------------------------------------------------
    # Processing-pipeline observer contract
    # ------------------------------------------------------------------

    def stage_started(
        self,
        context: ProcessingContext,
        stage_name: str,
    ) -> None:
        """Create/start the durable job for a processing-pipeline stage."""

        stage = self._resolve_stage(stage_name)
        self.start_stage(
            ingestion_id=self._ingestion_id(context),
            stage=stage,
        )

    def stage_completed(
        self,
        context: ProcessingContext,
        stage_name: str,
    ) -> None:
        """Complete the durable job and record an appropriate count."""

        stage = self._resolve_stage(stage_name)
        if stage in self._DEFERRED_COMPLETION_STAGES:
            # The persistence layer owns the durable checkpoint. It will call
            # complete_stage() after the chunk records are committed.
            return

        self.complete_stage(
            ingestion_id=self._ingestion_id(context),
            stage=stage,
            records_processed=self._records_processed(context, stage),
        )

    def stage_failed(
        self,
        context: ProcessingContext,
        stage_name: str,
        exception: Exception,
    ) -> None:
        """Fail the durable job for a processing-pipeline stage."""

        stage = self._resolve_stage(stage_name)
        self.fail_stage(
            ingestion_id=self._ingestion_id(context),
            stage=stage,
            exception=exception,
        )

    # ------------------------------------------------------------------
    # Event integration
    # ------------------------------------------------------------------

    def _record_started(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        retry_count: int,
    ) -> None:
        if self._event_service is None:
            return
        self._event_service.stage_started(
            ingestion_id=ingestion_id,
            stage=stage,
            sequence_number=self._STAGE_SEQUENCE[stage],
            retry_count=retry_count,
        )

    def _record_completed(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        duration_ms: int,
        records_processed: int,
        retry_count: int,
    ) -> None:
        if self._event_service is None:
            return
        self._event_service.stage_completed(
            ingestion_id=ingestion_id,
            stage=stage,
            duration_ms=duration_ms,
            records_processed=records_processed,
            retry_count=retry_count,
        )

    def _record_failed(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        duration_ms: int,
        exception: Exception,
        retry_count: int,
    ) -> None:
        if self._event_service is None:
            return
        self._event_service.stage_failed(
            ingestion_id=ingestion_id,
            stage=stage,
            duration_ms=duration_ms,
            exception=exception,
            retry_count=retry_count,
        )

    def _record_retry_requested(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        retry_count: int,
    ) -> None:
        if self._event_service is None:
            return
        self._event_service.stage_retry_requested(
            ingestion_id=ingestion_id,
            stage=stage,
            retry_count=retry_count,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ingestion_id(context: ProcessingContext) -> UUID:
        """Read the durable ingestion ID from processing metadata."""

        value = context.get_metadata("ingestion_id")
        if value is None:
            raise ValueError(
                "ProcessingContext does not contain an ingestion_id."
            )
        return UUID(str(value))

    @classmethod
    def _resolve_stage(cls, stage_name: str) -> PipelineStage:
        try:
            return cls._STAGE_ALIASES[stage_name]
        except KeyError as exc:
            raise ValueError(
                f"No ProcessingJob stage mapping exists for pipeline stage "
                f"'{stage_name}'."
            ) from exc

    @staticmethod
    def _records_processed(
        context: ProcessingContext,
        stage: PipelineStage,
    ) -> int:
        if stage == PipelineStage.VALIDATION:
            return 1
        if stage == PipelineStage.EXTRACTION:
            return (
                len(context.parsed_document.pages)
                if context.parsed_document
                else 0
            )
        if stage == PipelineStage.CHUNKING:
            return context.chunk_count
        return 0

    def _get_active_job(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
    ) -> tuple[ProcessingJob, datetime]:
        try:
            return self._active[stage]
        except KeyError as exc:
            raise RuntimeError(
                f"No active processing job exists for stage '{stage.value}' "
                f"and ingestion '{ingestion_id}'."
            ) from exc

    def close(self) -> None:
        """Close processing-job and event persistence sessions."""

        self._repository.close()
        if self._event_service is not None:
            self._event_service.close()


__all__ = [
    "ProcessingJobService",
]
