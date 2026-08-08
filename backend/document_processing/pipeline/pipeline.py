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
    ) -> ProcessingResult:
        """
        Execute the processing pipeline.
        """

        if not self._stages:
            raise PipelineConfigurationError("Processing pipeline contains no stages.")

        started_at = datetime.utcnow()

        completed_stage: str | None = None

        try:
            for stage in self._stages:
                stage(context)
                completed_stage = stage.name

            return ProcessingResult.completed(
                stage=completed_stage or "",
                duration=datetime.utcnow() - started_at,
            )

        except Exception as ex:
            failed_stage = context.current_stage or completed_stage or "Unknown"

            return ProcessingResult.failed_result(
                stage=failed_stage,
                exception=StageExecutionError(
                    failed_stage,
                    ex,
                ),
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
