"""
backend/operations/providers/logging_provider.py

Operation logging provider.
"""

from __future__ import annotations

from dataclasses import asdict

from backend.common.logging.logger import get_operations_logger
from backend.operations.models import OperationRecord
from backend.operations.providers.base import BaseOperationProvider


class LoggingProvider(BaseOperationProvider):
    """
    Publishes operation records to the Operations Logger.
    """

    def __init__(self) -> None:
        """
        Initialize the logging provider.
        """

        self._logger = get_operations_logger()

    def publish(
        self,
        record: OperationRecord,
    ) -> None:
        """
        Publish an operation record.
        """

        payload = asdict(record)

        payload["operation_type"] = record.operation_type.value
        payload["status"] = record.status.value

        payload["start_time"] = (
            record.start_time.isoformat() if record.start_time else None
        )

        payload["end_time"] = record.end_time.isoformat() if record.end_time else None

        self._logger.info(payload)


__all__ = [
    "LoggingProvider",
]
