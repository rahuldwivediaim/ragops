"""Durable pipeline-event tracking for ingestion observability."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from backend.document_processing.pipeline.context import ProcessingContext
from backend.models.enums import PipelineStage
from backend.models.pipeline_event import PipelineEvent
from backend.repositories.pipeline_event_repository import PipelineEventRepository

logger = logging.getLogger(__name__)


class PipelineEventService:
    """Persist an append-only operational history for ingestion stages.

    Pipeline-event persistence is intentionally non-blocking for the business
    ingestion path. A failure to write an observability event is logged and
    does not turn an otherwise successful processing stage into a failed stage.
    The event session is isolated from the ingestion and processing-job
    sessions so observability failures cannot corrupt those transactions.
    """

    STAGE_STARTED = "STAGE_STARTED"
    STAGE_COMPLETED = "STAGE_COMPLETED"
    STAGE_FAILED = "STAGE_FAILED"
    STAGE_RETRY_REQUESTED = "STAGE_RETRY_REQUESTED"

    _STAGE_ALIASES: dict[str, PipelineStage] = {
        "Validation": PipelineStage.VALIDATION,
        "Parsing": PipelineStage.EXTRACTION,
        "Chunking": PipelineStage.CHUNKING,
    }

    def __init__(self, repository: PipelineEventRepository) -> None:
        self._repository = repository

    def stage_started(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        sequence_number: int,
        retry_count: int,
    ) -> PipelineEvent | None:
        """Record the start of a processing stage."""

        return self._safe_create(
            ingestion_id=ingestion_id,
            stage=stage,
            event_type=self.STAGE_STARTED,
            message=f"{stage.value.title()} stage started.",
            details={
                "sequence_number": sequence_number,
                "retry_count": retry_count,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def stage_completed(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        duration_ms: int,
        records_processed: int,
        retry_count: int,
    ) -> PipelineEvent | None:
        """Record successful completion of a processing stage."""

        return self._safe_create(
            ingestion_id=ingestion_id,
            stage=stage,
            event_type=self.STAGE_COMPLETED,
            message=(
                f"{stage.value.title()} stage completed successfully."
            ),
            details={
                "duration_ms": max(duration_ms, 0),
                "records_processed": max(records_processed, 0),
                "retry_count": retry_count,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def stage_failed(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        duration_ms: int,
        exception: Exception,
        retry_count: int,
    ) -> PipelineEvent | None:
        """Record failure of a processing stage without persisting a traceback."""

        return self._safe_create(
            ingestion_id=ingestion_id,
            stage=stage,
            event_type=self.STAGE_FAILED,
            message=f"{stage.value.title()} stage failed.",
            details={
                "duration_ms": max(duration_ms, 0),
                "retry_count": retry_count,
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def stage_retry_requested(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        retry_count: int,
    ) -> PipelineEvent | None:
        """Record a request to retry a previously failed stage."""

        return self._safe_create(
            ingestion_id=ingestion_id,
            stage=stage,
            event_type=self.STAGE_RETRY_REQUESTED,
            message=f"Retry requested for {stage.value.title()} stage.",
            details={
                "retry_count": retry_count,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def stage_started_by_name(
        self,
        *,
        context: ProcessingContext,
        stage_name: str,
        sequence_number: int,
        retry_count: int,
    ) -> PipelineEvent | None:
        """Record a start event for a pipeline stage name."""

        return self.stage_started(
            ingestion_id=self._ingestion_id(context),
            stage=self.resolve_stage(stage_name),
            sequence_number=sequence_number,
            retry_count=retry_count,
        )

    @classmethod
    def resolve_stage(cls, stage_name: str) -> PipelineStage:
        """Map a processing-stage name to its durable pipeline stage."""

        try:
            return cls._STAGE_ALIASES[stage_name]
        except KeyError as exc:
            raise ValueError(
                f"No PipelineEvent stage mapping exists for pipeline stage "
                f"'{stage_name}'."
            ) from exc

    @staticmethod
    def _ingestion_id(context: ProcessingContext) -> UUID:
        value = context.get_metadata("ingestion_id")
        if value is None:
            raise ValueError(
                "ProcessingContext does not contain an ingestion_id."
            )
        return UUID(str(value))

    def _safe_create(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        event_type: str,
        message: str,
        details: dict[str, Any],
    ) -> PipelineEvent | None:
        """Persist an event without allowing observability to break ingestion."""

        try:
            return self._repository.create_event(
                ingestion_id=ingestion_id,
                stage=stage,
                event_type=event_type,
                message=message,
                details=details,
            )
        except Exception:
            logger.exception(
                "Failed to persist pipeline event.",
                extra={
                    "ingestion_id": str(ingestion_id),
                    "stage": stage.value,
                    "event_type": event_type,
                },
            )
            return None

    def close(self) -> None:
        """Close the event repository session."""

        self._repository.close()


__all__ = [
    "PipelineEventService",
]
