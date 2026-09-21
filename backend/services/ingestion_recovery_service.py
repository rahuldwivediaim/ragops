"""Derive safe, stage-aware recovery plans for ingestion executions."""

from __future__ import annotations

from uuid import UUID

from backend.models.enums import IngestionStatus, PipelineStage, ProcessingJobStatus
from backend.repositories.processing_job_repository import ProcessingJobRepository
from backend.schemas.ingestion_recovery import (
    IngestionRecoveryPlan,
    RecoveryAction,
)


class IngestionRecoveryService:
    """Calculate recovery options without executing any recovery action.

    The service deliberately derives the plan from persisted ProcessingJob state.
    It does not mutate ingestion data, invoke providers, or perform retries.
    """

    _EXECUTABLE_STAGES = (
        PipelineStage.VALIDATION,
        PipelineStage.EXTRACTION,
        PipelineStage.CHUNKING,
        PipelineStage.EMBEDDING,
        PipelineStage.INDEXING,
    )

    # A completed chunking stage is a durable checkpoint because Change #4
    # commits chunk rows before downstream embedding/indexing begins.
    _DURABLE_CHECKPOINTS = {PipelineStage.CHUNKING}

    def __init__(self, processing_job_repository: ProcessingJobRepository) -> None:
        self._repository = processing_job_repository

    def build_plan(
        self,
        *,
        ingestion_id: UUID,
        ingestion_status: IngestionStatus,
    ) -> IngestionRecoveryPlan:
        """Build a deterministic recovery plan from persisted stage state."""
        jobs = self._repository.list_by_ingestion(ingestion_id=ingestion_id)
        failed_job = next(
            (job for job in jobs if job.status == ProcessingJobStatus.FAILED),
            None,
        )
        completed_stages = {
            job.stage
            for job in jobs
            if job.status == ProcessingJobStatus.COMPLETED
            and job.stage in self._EXECUTABLE_STAGES
        }
        last_executed = self._last_stage(jobs)
        last_durable = self._last_durable_checkpoint(completed_stages)

        if ingestion_status == IngestionStatus.COMPLETED and failed_job is None:
            return IngestionRecoveryPlan(
                ingestion_id=ingestion_id,
                ingestion_status=ingestion_status,
                last_executed_stage=last_executed,
                last_durable_checkpoint=last_durable,
                retryable=False,
                requires_rebuild=False,
                requires_vector_reconciliation=False,
                recommended_action=RecoveryAction.NONE,
                message="Ingestion completed successfully; no recovery action is required.",
            )

        if failed_job is None:
            return IngestionRecoveryPlan(
                ingestion_id=ingestion_id,
                ingestion_status=ingestion_status,
                last_executed_stage=last_executed,
                last_durable_checkpoint=last_durable,
                retryable=False,
                requires_rebuild=False,
                requires_vector_reconciliation=False,
                recommended_action=RecoveryAction.NONE,
                message="No failed processing stage is available for recovery.",
            )

        failed_stage = failed_job.stage
        if failed_stage == PipelineStage.VALIDATION:
            return self._plan(
                ingestion_id,
                ingestion_status,
                failed_stage,
                last_executed,
                last_durable,
                RecoveryAction.RETRY_VALIDATION,
                "Validation failed; retry validation if the failure is transient, otherwise fix the document and reprocess it.",
                retryable=True,
            )

        if failed_stage == PipelineStage.EXTRACTION:
            return self._plan(
                ingestion_id,
                ingestion_status,
                failed_stage,
                last_executed,
                last_durable,
                RecoveryAction.RETRY_EXTRACTION,
                "Extraction failed; retry extraction if the failure is transient, otherwise fix the document and reprocess it.",
                retryable=True,
            )

        if failed_stage == PipelineStage.CHUNKING:
            return self._plan(
                ingestion_id,
                ingestion_status,
                failed_stage,
                last_executed,
                last_durable,
                RecoveryAction.RETRY_EXTRACTION,
                "Chunking failed before a durable chunk checkpoint was established; recovery must restart from extraction.",
                retryable=True,
            )

        if failed_stage == PipelineStage.EMBEDDING:
            return self._plan(
                ingestion_id,
                ingestion_status,
                failed_stage,
                last_executed,
                last_durable,
                RecoveryAction.RETRY_EMBEDDING,
                "Embedding failed; durable chunks are preserved and embedding can be regenerated without reprocessing the document.",
                retryable=True,
            )

        if failed_stage == PipelineStage.INDEXING:
            return self._plan(
                ingestion_id,
                ingestion_status,
                failed_stage,
                last_executed,
                last_durable,
                RecoveryAction.RETRY_FROM_EMBEDDING,
                "Vector indexing failed; embedding vectors are not a durable payload, so embeddings must be regenerated before indexing is retried.",
                retryable=True,
                requires_rebuild=True,
                requires_vector_reconciliation=True,
            )

        return self._plan(
            ingestion_id,
            ingestion_status,
            failed_stage,
            last_executed,
            last_durable,
            RecoveryAction.NONE,
            "The failed stage is not currently supported for automated recovery.",
            retryable=False,
        )

    def _plan(
        self,
        ingestion_id: UUID,
        ingestion_status: IngestionStatus,
        failed_stage: PipelineStage,
        last_executed_stage: PipelineStage | None,
        last_durable_checkpoint: PipelineStage | None,
        action: RecoveryAction,
        message: str,
        *,
        retryable: bool,
        requires_rebuild: bool = False,
        requires_vector_reconciliation: bool = False,
    ) -> IngestionRecoveryPlan:
        recovery_stage = {
            RecoveryAction.RETRY_VALIDATION: PipelineStage.VALIDATION,
            RecoveryAction.RETRY_EXTRACTION: PipelineStage.EXTRACTION,
            RecoveryAction.RETRY_EMBEDDING: PipelineStage.EMBEDDING,
            RecoveryAction.RETRY_FROM_EMBEDDING: PipelineStage.EMBEDDING,
        }.get(action)
        return IngestionRecoveryPlan(
            ingestion_id=ingestion_id,
            ingestion_status=ingestion_status,
            failed_stage=failed_stage,
            last_executed_stage=last_executed_stage,
            last_durable_checkpoint=last_durable_checkpoint,
            recovery_stage=recovery_stage,
            retryable=retryable,
            requires_rebuild=requires_rebuild,
            requires_vector_reconciliation=requires_vector_reconciliation,
            recommended_action=action,
            message=message,
        )

    def _last_stage(self, jobs: list) -> PipelineStage | None:
        stages = [job.stage for job in jobs if job.stage in self._EXECUTABLE_STAGES]
        if not stages:
            return None
        return max(stages, key=lambda stage: self._EXECUTABLE_STAGES.index(stage))

    def _last_durable_checkpoint(
        self, completed_stages: set[PipelineStage]
    ) -> PipelineStage | None:
        checkpoints = [stage for stage in completed_stages if stage in self._DURABLE_CHECKPOINTS]
        if not checkpoints:
            return None
        return max(checkpoints, key=lambda stage: self._EXECUTABLE_STAGES.index(stage))
