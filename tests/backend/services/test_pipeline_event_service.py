from __future__ import annotations

from unittest.mock import Mock
from uuid import uuid4

from backend.models.enums import PipelineStage
from backend.services.pipeline_event_service import PipelineEventService


def test_stage_started_persists_structured_event_details() -> None:
    repository = Mock()
    repository.create_event.return_value = object()
    service = PipelineEventService(repository)
    ingestion_id = uuid4()

    result = service.stage_started(
        ingestion_id=ingestion_id,
        stage=PipelineStage.VALIDATION,
        sequence_number=1,
        retry_count=0,
    )

    assert result is not None
    repository.create_event.assert_called_once()
    kwargs = repository.create_event.call_args.kwargs
    assert kwargs["ingestion_id"] == ingestion_id
    assert kwargs["stage"] == PipelineStage.VALIDATION
    assert kwargs["event_type"] == "STAGE_STARTED"
    assert kwargs["details"]["sequence_number"] == 1
    assert kwargs["details"]["retry_count"] == 0


def test_stage_failed_does_not_expose_traceback_details() -> None:
    repository = Mock()
    repository.create_event.return_value = object()
    service = PipelineEventService(repository)

    service.stage_failed(
        ingestion_id=uuid4(),
        stage=PipelineStage.INDEXING,
        duration_ms=42,
        exception=ValueError("temporary failure"),
        retry_count=1,
    )

    details = repository.create_event.call_args.kwargs["details"]
    assert details["error_type"] == "ValueError"
    assert details["error_message"] == "temporary failure"
    assert "traceback" not in details


def test_event_persistence_failure_is_non_blocking() -> None:
    repository = Mock()
    repository.create_event.side_effect = RuntimeError("database unavailable")
    service = PipelineEventService(repository)

    result = service.stage_completed(
        ingestion_id=uuid4(),
        stage=PipelineStage.CHUNKING,
        duration_ms=100,
        records_processed=90,
        retry_count=0,
    )

    assert result is None
