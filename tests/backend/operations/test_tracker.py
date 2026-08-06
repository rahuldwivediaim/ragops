"""
Unit tests for the OperationTracker.
"""

from __future__ import annotations

from backend.operations.enums import (
    OperationStatus,
    OperationType,
)
from backend.operations.models import OperationRecord
from backend.operations.providers.base import BaseOperationProvider
from backend.operations.tracker import OperationTracker


class InMemoryProvider(BaseOperationProvider):
    """
    Test provider that stores published records in memory.
    """

    def __init__(self) -> None:
        self.records: list[OperationRecord] = []

    def publish(self, record: OperationRecord) -> None:
        self.records.append(record)


def test_start_operation() -> None:
    """
    Verify a STARTED record is published correctly.
    """

    provider = InMemoryProvider()

    tracker = OperationTracker(
        providers=[provider],
    )

    context = tracker.start(
        operation_type=OperationType.DOCUMENT_INGESTION,
        user_id="user1",
        resource_id="doc-100",
        resource_name="Employee Handbook.pdf",
    )

    assert len(provider.records) == 1

    record = provider.records[0]

    assert record.status == OperationStatus.STARTED
    assert record.operation_type == OperationType.DOCUMENT_INGESTION
    assert record.user_id == "user1"
    assert record.resource_id == "doc-100"
    assert record.resource_name == "Employee Handbook.pdf"

    assert record.end_time is None
    assert record.duration_ms is None

    assert context.operation_id == record.operation_id
    assert context.correlation_id == record.correlation_id


def test_complete_operation() -> None:
    """
    Verify a SUCCESS record is published.
    """

    provider = InMemoryProvider()

    tracker = OperationTracker(
        providers=[provider],
    )

    context = tracker.start(
        operation_type=OperationType.QUERY,
    )

    tracker.complete(
        context,
        message="Completed successfully.",
    )

    assert len(provider.records) == 2

    record = provider.records[-1]

    assert record.status == OperationStatus.SUCCESS
    assert record.message == "Completed successfully."

    assert record.end_time is not None
    assert record.duration_ms is not None
    assert record.duration_ms >= 0


def test_fail_operation() -> None:
    """
    Verify a FAILED record is published.
    """

    provider = InMemoryProvider()

    tracker = OperationTracker(
        providers=[provider],
    )

    context = tracker.start(
        operation_type=OperationType.LOGIN,
    )

    tracker.fail(
        context,
        exception=ValueError("Invalid credentials"),
    )

    assert len(provider.records) == 2

    record = provider.records[-1]

    assert record.status == OperationStatus.FAILED
    assert record.message == "Invalid credentials"

    assert record.end_time is not None
    assert record.duration_ms is not None


def test_existing_correlation_id_is_preserved() -> None:
    """
    Verify an existing correlation ID is reused.
    """

    provider = InMemoryProvider()

    tracker = OperationTracker(
        providers=[provider],
    )

    context = tracker.start(
        operation_type=OperationType.QUERY,
        correlation_id="abc-123",
    )

    assert context.correlation_id == "abc-123"

    record = provider.records[0]

    assert record.correlation_id == "abc-123"


def test_tracker_requires_provider() -> None:
    """
    Verify tracker cannot be created without providers.
    """

    try:
        OperationTracker(providers=[])
        assert False, "Expected ValueError"
    except ValueError:
        pass
