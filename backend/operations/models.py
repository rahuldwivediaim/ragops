"""
Data models for the Operations Framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from backend.operations.enums import OperationStatus, OperationType


@dataclass(frozen=True, slots=True)
class OperationRecord:
    """
    Immutable operation record published to one or more providers.
    """

    operation_id: str
    correlation_id: str

    operation_type: OperationType
    status: OperationStatus

    start_time: datetime
    end_time: datetime | None = None
    duration_ms: int | None = None

    user_id: str | None = None

    resource_id: str | None = None
    resource_name: str | None = None

    current_stage: str | None = None

    message: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OperationContext:
    """
    Mutable context representing an operation while it is executing.
    """

    operation_id: str
    correlation_id: str

    operation_type: OperationType
    status: OperationStatus

    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))

    user_id: str | None = None

    resource_id: str | None = None
    resource_name: str | None = None

    current_stage: str | None = None

    message: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def set_stage(self, stage: str) -> None:
        """
        Update the current execution stage.
        """
        self.current_stage = stage

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add or update operation metadata.
        """
        self.metadata[key] = value
