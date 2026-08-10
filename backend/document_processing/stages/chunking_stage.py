"""
File:
    backend/document_processing/stages/chunking_stage.py

Purpose:
    Generates chunks from a parsed document.

Responsibilities:

- Validate parsed document exists.
- Invoke configured chunker.
- Populate ProcessingContext.chunks.

Persistence is handled by the ingestion service.
"""

from __future__ import annotations

from backend.document_processing.chunker import Chunker
from backend.document_processing.pipeline import (
    ProcessingContext,
    ProcessingStage,
)


class ChunkingStage(ProcessingStage):
    """
    Pipeline stage responsible for document chunking.
    """

    def __init__(
        self,
        chunker: Chunker,
    ) -> None:
        self._chunker = chunker

    @property
    def name(self) -> str:
        return "Chunking"

    def execute(
        self,
        context: ProcessingContext,
    ) -> None:
        """
        Chunk the parsed document.
        """

        if context.parsed_document is None:
            raise ValueError("Parsed document not available.")

        context.chunks = self._chunker.chunk_document(context.parsed_document)

        context.add_metadata(
            "chunk_count",
            len(context.chunks),
        )


__all__ = [
    "ChunkingStage",
]
