from __future__ import annotations

from unittest.mock import ANY, Mock
from uuid import uuid4

from backend.models.enums import PipelineStage, ProcessingJobStatus
from backend.models.processing_job import ProcessingJob
from backend.services.processing_job_service import ProcessingJobService


def test_start_stage_creates_first_execution_with_zero_retries() -> None:
    ingestion_id = uuid4()
    repository = Mock()
    repository.get_by_ingestion_and_stage.return_value = None
    job = ProcessingJob(
        ingestion_id=ingestion_id,
        stage=PipelineStage.VALIDATION,
        status=ProcessingJobStatus.RUNNING,
        sequence_number=1,
        retry_count=0,
        records_processed=0,
    )
    repository.create_running.return_value = job

    service = ProcessingJobService(repository)
    result = service.start_stage(
        ingestion_id=ingestion_id, stage=PipelineStage.VALIDATION
    )

    assert result is job
    repository.create_running.assert_called_once_with(
        ingestion_id=ingestion_id,
        stage=PipelineStage.VALIDATION,
        sequence_number=1,
    )


def test_retry_reuses_failed_job_and_delegates_retry_state_to_repository() -> None:
    ingestion_id = uuid4()
    repository = Mock()
    job = ProcessingJob(
        ingestion_id=ingestion_id,
        stage=PipelineStage.INDEXING,
        status=ProcessingJobStatus.FAILED,
        sequence_number=5,
        retry_count=0,
        records_processed=0,
        error_message="temporary failure",
    )
    repository.get_by_ingestion_and_stage.return_value = job
    repository.mark_running.side_effect = lambda existing: existing

    service = ProcessingJobService(repository)
    result = service.start_stage(
        ingestion_id=ingestion_id, stage=PipelineStage.INDEXING
    )

    assert result is job
    repository.mark_running.assert_called_once_with(job)


def test_parsing_maps_to_extraction() -> None:
    repository = Mock()
    service = ProcessingJobService(repository)

    assert service._resolve_stage("Parsing") == PipelineStage.EXTRACTION


def test_chunking_completion_is_deferred_until_durable_checkpoint() -> None:
    ingestion_id = uuid4()
    repository = Mock()
    job = ProcessingJob(
        ingestion_id=ingestion_id,
        stage=PipelineStage.CHUNKING,
        status=ProcessingJobStatus.RUNNING,
        sequence_number=3,
        retry_count=0,
        records_processed=0,
    )
    repository.get_by_ingestion_and_stage.return_value = None
    repository.create_running.return_value = job

    service = ProcessingJobService(repository)

    context = Mock()
    context.get_metadata.return_value = str(ingestion_id)
    context.chunk_count = 10

    service.stage_started(context, "Chunking")
    service.stage_completed(context, "Chunking")

    repository.mark_completed.assert_not_called()

    service.complete_stage(
        ingestion_id=ingestion_id,
        stage=PipelineStage.CHUNKING,
        records_processed=10,
    )

    repository.mark_completed.assert_called_once_with(
        job,
        duration_ms=ANY,
        records_processed=10,
    )
