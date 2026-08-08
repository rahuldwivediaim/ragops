"""
File:
    backend/document_processing/pipeline/result.py

Purpose:
    Represents the outcome of executing a document processing pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any


@dataclass(slots=True)
class ProcessingResult:
    """
    Result returned by ProcessingPipeline.
    """

    # ------------------------------------------------------------------
    # Execution Status
    # ------------------------------------------------------------------

    success: bool = False

    # ------------------------------------------------------------------
    # Pipeline Information
    # ------------------------------------------------------------------

    completed_stage: str | None = None

    failed_stage: str | None = None

    # ------------------------------------------------------------------
    # Execution Metrics
    # ------------------------------------------------------------------

    duration: timedelta | None = None

    # ------------------------------------------------------------------
    # Error Information
    # ------------------------------------------------------------------

    exception: Exception | None = None

    message: str | None = None

    # ------------------------------------------------------------------
    # Additional Information
    # ------------------------------------------------------------------

    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    @property
    def failed(self) -> bool:
        """
        Returns True if pipeline execution failed.
        """

        return not self.success

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store additional execution metadata.
        """

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve execution metadata.
        """

        return self.metadata.get(key, default)

    @classmethod
    def completed(
        cls,
        *,
        stage: str,
        duration: timedelta,
    ) -> "ProcessingResult":
        """
        Create a successful pipeline result.
        """

        return cls(
            success=True,
            completed_stage=stage,
            duration=duration,
        )

    @classmethod
    def failed_result(
        cls,
        *,
        stage: str,
        exception: Exception,
        duration: timedelta,
    ) -> "ProcessingResult":
        """
        Create a failed pipeline result.
        """

        return cls(
            success=False,
            failed_stage=stage,
            exception=exception,
            message=str(exception),
            duration=duration,
        )

    def __repr__(self) -> str:
        return (
            "ProcessingResult("
            f"success={self.success}, "
            f"completed_stage={self.completed_stage}, "
            f"failed_stage={self.failed_stage})"
        )


__all__ = [
    "ProcessingResult",
]
