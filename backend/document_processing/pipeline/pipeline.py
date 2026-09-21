"""
File:
    backend/document_processing/pipeline/pipeline.py

Purpose:
    Orchestrates execution of document processing stages.
"""

from __future__ import annotations

from datetime import datetime

from .context import ProcessingContext
from .exceptions import (
    PipelineConfigurationError,
    StageExecutionError,
)
from .observer import ProcessingStageObserver
from .result import ProcessingResult
from .stage import ProcessingStage


class ProcessingPipeline:
    """
    Executes document processing stages sequentially.
    """

    def __init__(self) -> None:
        self._stages: list[ProcessingStage] = []

    # ------------------------------------------------------------------
    # Stage Registration
    # ------------------------------------------------------------------

    def add_stage(
        self,
        stage: ProcessingStage,
    ) -> "ProcessingPipeline":
        """
        Register a processing stage.

        Returns
        -------
        ProcessingPipeline
            Enables fluent pipeline construction.
        """

        if any(existing.name == stage.name for existing in self._stages):
            raise PipelineConfigurationError(
                f"Stage '{stage.name}' is already registered."
            )

        self._stages.append(stage)

        return self

    @property
    def stages(self) -> tuple[ProcessingStage, ...]:
        """
        Registered processing stages.
        """

        return tuple(self._stages)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        context: ProcessingContext,
        observer: ProcessingStageObserver | None = None,
    ) -> ProcessingResult:
        """
        Execute the processing pipeline sequentially.

        ``observer`` is intentionally optional so the processing framework
        remains usable without persistence or observability infrastructure.
        When supplied, it receives durable-lifecycle callbacks around each
        stage. Concrete observers decide how those callbacks are persisted.
        """

        if not self._stages:
            raise PipelineConfigurationError("Processing pipeline contains no stages.")

        started_at = datetime.utcnow()
        completed_stage: str | None = None

        for stage in self._stages:
            if observer is not None:
                observer.stage_started(context, stage.name)

            try:
                stage(context)
            except Exception as ex:
                if observer is not None:
                    observer.stage_failed(
                        context,
                        stage.name,
                        ex,
                    )

                failed_stage = context.current_stage or completed_stage or stage.name
                return ProcessingResult.failed_result(
                    stage=failed_stage,
                    exception=StageExecutionError(
                        failed_stage,
                        ex,
                    ),
                    duration=datetime.utcnow() - started_at,
                )

            if observer is not None:
                observer.stage_completed(
                    context,
                    stage.name,
                )

            completed_stage = stage.name

        return ProcessingResult.completed(
            stage=completed_stage or "",
            duration=datetime.utcnow() - started_at,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all registered stages.
        """

        self._stages.clear()

    def __len__(self) -> int:
        return len(self._stages)

    def __iter__(self):
        return iter(self._stages)

    def __repr__(self) -> str:
        stage_names = ", ".join(stage.name for stage in self._stages)

        return f"ProcessingPipeline(stages=[{stage_names}])"


__all__ = [
    "ProcessingPipeline",
]
