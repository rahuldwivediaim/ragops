"""
File:
    backend/document_processing/pipeline/exceptions.py

Purpose:
    Exceptions raised by the document processing pipeline.
"""

from __future__ import annotations


class PipelineError(Exception):
    """
    Base exception for all pipeline-related errors.
    """


class StageExecutionError(PipelineError):
    """
    Raised when a processing stage fails.

    Attributes
    ----------
    stage_name
        Name of the stage that failed.

    original_exception
        Original exception raised by the stage.
    """

    def __init__(
        self,
        stage_name: str,
        original_exception: Exception,
    ) -> None:
        self.stage_name = stage_name
        self.original_exception = original_exception

        super().__init__(f"Stage '{stage_name}' failed: {original_exception}")


class PipelineConfigurationError(PipelineError):
    """
    Raised when the processing pipeline has been configured incorrectly.
    """

    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(message)


__all__ = [
    "PipelineError",
    "StageExecutionError",
    "PipelineConfigurationError",
]
