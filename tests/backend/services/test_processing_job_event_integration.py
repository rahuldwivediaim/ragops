from __future__ import annotations

from unittest.mock import Mock
from uuid import uuid4

from backend.models.enums import PipelineStage, ProcessingJobStatus
from backend.models.processing_job import ProcessingJob
from backend.services.processing_job_service import ProcessingJobService


def test_processing_job_start_emits_stage_started_event() -> None:
    ingestion_id = uuid4()
    repository = Mock()
    event_service = Mock()
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

    service = ProcessingJobService(repository, event_service=event_service)
    service.start_stage(
        ingestion_id=ingestion_id,
        stage=PipelineStage.VALIDATION,
    )

    event_service.stage_started.assert_called_once_with(
        ingestion_id=ingestion_id,
        stage=PipelineStage.VALIDATION,
        sequence_number=1,
        retry_count=0,
    )


def test_processing_job_completion_emits_stage_completed_event() -> None:
    ingestion_id = uuid4()
    repository = Mock()
    event_service = Mock()
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
    def complete(existing, **kwargs):
        existing.status = ProcessingJobStatus.COMPLETED
        existing.duration_ms = kwargs["duration_ms"]
        existing.records_processed = kwargs["records_processed"]
        return existing

    repository.mark_completed.side_effect = complete

    service = ProcessingJobService(repository, event_service=event_service)
    service.start_stage(
        ingestion_id=ingestion_id,
        stage=PipelineStage.CHUNKING,
    )
    service.complete_stage(
        ingestion_id=ingestion_id,
        stage=PipelineStage.CHUNKING,
        records_processed=90,
    )

    event_service.stage_completed.assert_called_once()
    kwargs = event_service.stage_completed.call_args.kwargs
    assert kwargs["ingestion_id"] == ingestion_id
    assert kwargs["stage"] == PipelineStage.CHUNKING
    assert kwargs["records_processed"] == 90
