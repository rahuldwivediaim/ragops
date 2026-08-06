"""
Business operation tracking framework.

This package provides a lightweight framework for tracking the lifecycle
of business operations across the application.

Typical usage:

    from backend.operations import (
        OperationTracker,
        OperationType,
        OperationStatus,
        OperationContext,
    )
"""

from backend.operations.enums import (
    OperationProvider,
    OperationStatus,
    OperationType,
)
from backend.operations.models import (
    OperationContext,
    OperationRecord,
)
from backend.operations.tracker import OperationTracker

__all__ = [
    "OperationContext",
    "OperationProvider",
    "OperationRecord",
    "OperationStatus",
    "OperationTracker",
    "OperationType",
]
