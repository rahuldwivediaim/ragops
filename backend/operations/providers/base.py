"""
Base contract for all operation providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.operations.models import OperationRecord


class BaseOperationProvider(ABC):
    """
    Abstract base class for all operation providers.

    Examples:
        - ConsoleProvider
        - FileProvider
        - DatabaseProvider
    """

    @abstractmethod
    def publish(self, record: OperationRecord) -> None:
        """
        Publish an operation record.

        Args:
            record: Immutable operation record.
        """
        raise NotImplementedError
