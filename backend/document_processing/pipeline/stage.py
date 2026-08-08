"""
File:
    backend/document_processing/pipeline/stage.py

Purpose:
    Defines the base contract for all document processing stages.

Each stage performs one well-defined responsibility within the
processing pipeline.

Examples:

- ValidationStage
- ParsingStage
- ChunkingStage
- EmbeddingStage
- IndexingStage

Stages should contain business logic.

The pipeline is responsible only for orchestration.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .context import ProcessingContext


class ProcessingStage(ABC):
    """
    Base class for all document processing stages.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable stage name.
        """

    @abstractmethod
    def execute(
        self,
        context: ProcessingContext,
    ) -> None:
        """
        Execute the processing stage.

        Parameters
        ----------
        context
            Shared processing context.

        Raises
        ------
        Exception
            Any unrecoverable processing error.
        """

    def before_execute(
        self,
        context: ProcessingContext,
    ) -> None:
        """
        Hook executed immediately before the stage runs.

        Subclasses may override.
        """

        context.set_stage(self.name)

    def after_execute(
        self,
        context: ProcessingContext,
    ) -> None:
        """
        Hook executed after successful completion.

        Subclasses may override.
        """

        return

    def __call__(
        self,
        context: ProcessingContext,
    ) -> None:
        """
        Execute the complete stage lifecycle.
        """

        self.before_execute(context)
        self.execute(context)
        self.after_execute(context)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


__all__ = [
    "ProcessingStage",
]
