"""
Observer contract for document processing stage execution.

The processing pipeline remains provider- and persistence-agnostic. Concrete
observers can record operational state without coupling the pipeline to
SQLAlchemy or a particular observability backend.
"""

from __future__ import annotations

from typing import Protocol

from .context import ProcessingContext


class ProcessingStageObserver(Protocol):
    """Observer notified around each processing-stage execution."""

    def stage_started(
        self,
        context: ProcessingContext,
        stage_name: str,
    ) -> None:
        """Called immediately before a stage executes."""

    def stage_completed(
        self,
        context: ProcessingContext,
        stage_name: str,
    ) -> None:
        """Called after a stage completes successfully."""

    def stage_failed(
        self,
        context: ProcessingContext,
        stage_name: str,
        exception: Exception,
    ) -> None:
        """Called when a stage raises an exception."""
