"""
File:
    backend/document_processing/stages/validation_stage.py

Purpose:
    Performs the initial validation of a document before processing
    begins.

Responsibilities:

- Verify source file exists.
- Verify source is a file.
- Verify source file is not empty.

This stage intentionally performs only lightweight validation.
Business validation belongs elsewhere.
"""

from __future__ import annotations

from backend.document_processing.pipeline import (
    ProcessingContext,
    ProcessingStage,
)


class ValidationStage(ProcessingStage):
    """
    Validates the document before processing.
    """

    @property
    def name(self) -> str:
        return "Validation"

    def execute(
        self,
        context: ProcessingContext,
    ) -> None:
        """
        Validate the source document.
        """

        source = context.source_file

        if not source.exists():
            raise FileNotFoundError(source)

        if not source.is_file():
            raise ValueError(f"{source} is not a file.")

        if source.stat().st_size == 0:
            raise ValueError("Document is empty.")

        context.add_metadata(
            "file_size_bytes",
            source.stat().st_size,
        )

        context.add_metadata(
            "validated",
            True,
        )


__all__ = [
    "ValidationStage",
]
