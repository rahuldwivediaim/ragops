from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from backend.models.enums import IngestionStatus, PipelineStage, ProcessingJobStatus
from backend.schemas.ingestion_recovery import RecoveryAction
from backend.services.ingestion_recovery_service import IngestionRecoveryService


def _job(stage: PipelineStage, status: ProcessingJobStatus):
    return SimpleNamespace(stage=stage, status=status, sequence_number=1)


def _service(jobs):
    repository = SimpleNamespace(list_by_ingestion=lambda *, ingestion_id: jobs)
    return IngestionRecoveryService(repository)


def test_completed_ingestion_has_no_recovery_plan():
    ingestion_id = uuid4()
    plan = _service(
        [
            _job(PipelineStage.VALIDATION, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.EXTRACTION, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.CHUNKING, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.EMBEDDING, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.INDEXING, ProcessingJobStatus.COMPLETED),
        ]
    ).build_plan(ingestion_id=ingestion_id, ingestion_status=IngestionStatus.COMPLETED)

    assert plan.retryable is False
    assert plan.recommended_action == RecoveryAction.NONE
    assert plan.last_durable_checkpoint == PipelineStage.CHUNKING


def test_embedding_failure_recovers_from_embedding_using_durable_chunks():
    ingestion_id = uuid4()
    plan = _service(
        [
            _job(PipelineStage.VALIDATION, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.EXTRACTION, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.CHUNKING, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.EMBEDDING, ProcessingJobStatus.FAILED),
        ]
    ).build_plan(ingestion_id=ingestion_id, ingestion_status=IngestionStatus.FAILED)

    assert plan.failed_stage == PipelineStage.EMBEDDING
    assert plan.last_durable_checkpoint == PipelineStage.CHUNKING
    assert plan.recovery_stage == PipelineStage.EMBEDDING
    assert plan.retryable is True
    assert plan.requires_rebuild is False
    assert plan.recommended_action == RecoveryAction.RETRY_EMBEDDING


def test_indexing_failure_requires_embedding_rebuild_and_reconciliation():
    ingestion_id = uuid4()
    plan = _service(
        [
            _job(PipelineStage.VALIDATION, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.EXTRACTION, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.CHUNKING, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.EMBEDDING, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.INDEXING, ProcessingJobStatus.FAILED),
        ]
    ).build_plan(ingestion_id=ingestion_id, ingestion_status=IngestionStatus.FAILED)

    assert plan.failed_stage == PipelineStage.INDEXING
    assert plan.last_durable_checkpoint == PipelineStage.CHUNKING
    assert plan.recovery_stage == PipelineStage.EMBEDDING
    assert plan.requires_rebuild is True
    assert plan.requires_vector_reconciliation is True
    assert plan.recommended_action == RecoveryAction.RETRY_FROM_EMBEDDING


def test_chunking_failure_restarts_from_extraction():
    ingestion_id = uuid4()
    plan = _service(
        [
            _job(PipelineStage.VALIDATION, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.EXTRACTION, ProcessingJobStatus.COMPLETED),
            _job(PipelineStage.CHUNKING, ProcessingJobStatus.FAILED),
        ]
    ).build_plan(ingestion_id=ingestion_id, ingestion_status=IngestionStatus.FAILED)

    assert plan.last_durable_checkpoint is None
    assert plan.recovery_stage == PipelineStage.EXTRACTION
    assert plan.recommended_action == RecoveryAction.RETRY_EXTRACTION
