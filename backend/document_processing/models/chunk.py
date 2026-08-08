"""
Chunk model used by the document processing pipeline.

Unlike backend.models.chunk, this class is NOT persisted.

It represents a chunk while it moves through the processing pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Chunk:
    """
    In-memory chunk produced by the chunking stage.
    """

    chunk_number: int

    page_number: int

    text: str

    character_start: int

    character_end: int

    token_count: int | None = None

    metadata: dict[str, str] | None = None


__all__ = [
    "Chunk",
]
