"""
Operation Tracker implementation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.operations.enums import OperationStatus, OperationType
from backend.operations.models import OperationContext, OperationRecord
from backend.operations.providers.base import BaseOperationProvider


class OperationTracker:
    """
    Tracks the lifecycle of business operations.

    Responsibilities:
        - Start operations
        - Complete operations
        - Fail operations
        - Publish operation records to configured providers
    """

    def __init__(
        self,
        providers: list[BaseOperationProvider],
    ) -> None:
        """
        Initialize the operation tracker.

        Args:
            providers:
                Providers that will receive published operation records.
        """

        self._providers = list(providers)

        if not self._providers:
            raise ValueError("At least one operation provider must be configured.")

    def start(
        self,
        operation_type: OperationType,
        *,
        user_id: str | None = None,
        resource_id: str | None = None,
        resource_name: str | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> OperationContext:
        """
        Start a new business operation.

        Args:
            operation_type:
                Type of business operation.

            user_id:
                User initiating the operation.

            resource_id:
                System identifier of the resource.

            resource_name:
                Human-readable resource name.

            correlation_id:
                Existing correlation identifier. If omitted,
                a new identifier is generated.
            metadata:
                Additional metadata associated with the operation.

        Returns:
            Mutable operation context.
        """

        context = OperationContext(
            operation_id=str(uuid4()),
            correlation_id=correlation_id or str(uuid4()),
            operation_type=operation_type,
            status=OperationStatus.STARTED,
            user_id=user_id,
            resource_id=resource_id,
            resource_name=resource_name,
            metadata=dict(metadata or {}),
        )

        self._publish(self._create_record(context))

        return context

    def complete(
        self,
        context: OperationContext,
        message: str | None = None,
    ) -> None:
        """
        Mark an operation as successful.
        """

        context.status = OperationStatus.SUCCESS

        if message is not None:
            context.message = message

        self._publish(self._create_record(context))

    def fail(
        self,
        context: OperationContext,
        *,
        exception: Exception | None = None,
        message: str | None = None,
    ) -> None:
        """
        Mark an operation as failed.
        """

        context.status = OperationStatus.FAILED

        if exception is not None:
            context.message = str(exception)
        elif message is not None:
            context.message = message

        self._publish(self._create_record(context))

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _create_record(
        self,
        context: OperationContext,
    ) -> OperationRecord:
        """
        Convert a mutable OperationContext into an immutable
        OperationRecord.
        """

        if context.status == OperationStatus.STARTED:
            end_time = None
            duration_ms = None
        else:
            end_time = datetime.now(UTC)

            duration_ms = int((end_time - context.start_time).total_seconds() * 1000)

        return OperationRecord(
            operation_id=context.operation_id,
            correlation_id=context.correlation_id,
            operation_type=context.operation_type,
            status=context.status,
            start_time=context.start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            user_id=context.user_id,
            resource_id=context.resource_id,
            resource_name=context.resource_name,
            current_stage=context.current_stage,
            message=context.message,
            metadata=dict(context.metadata),
        )

    def _publish(
        self,
        record: OperationRecord,
    ) -> None:
        """
        Publish an operation record to every configured provider.
        """

        for provider in self._providers:
            try:
                provider.publish(record)
            except Exception:
                # TODO:
                # Replace with the project's technical logging
                # framework once it is implemented.
                pass


__all__ = [
    "OperationTracker",
]
