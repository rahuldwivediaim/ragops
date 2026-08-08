"""
File:
    backend/document_processing/pipeline/context.py

Purpose:
    Shared context passed between all document processing stages.

Each stage enriches the context as the document progresses through the
processing pipeline.

The context represents the complete processing state of a document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from backend.document_processing.models.chunk import Chunk
from uuid import UUID

from backend.document_processing.models.parsed_document import ParsedDocument
from backend.models.document_parsing_metadata import (
    DocumentParsingMetadata,
)


@dataclass(slots=True)
class ProcessingContext:
    """
    Shared context for the document processing pipeline.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    document_id: UUID

    document_version_id: UUID

    knowledge_base_id: UUID

    # ------------------------------------------------------------------
    # Source
    # ------------------------------------------------------------------

    source_file: Path

    # ------------------------------------------------------------------
    # Processing Results
    # ------------------------------------------------------------------

    parsed_document: ParsedDocument | None = None

    parsing_metadata: DocumentParsingMetadata | None = None

    chunks: list[Chunk] = field(default_factory=list)

    embeddings: list[Any] = field(default_factory=list)

    vectors: list[Any] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Runtime Metadata
    # ------------------------------------------------------------------

    metadata: dict[str, Any] = field(default_factory=dict)

    current_stage: str | None = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def set_stage(
        self,
        stage_name: str,
    ) -> None:
        """
        Update the currently executing pipeline stage.
        """

        self.current_stage = stage_name

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store runtime pipeline metadata.

        This metadata is intended for execution information only.
        Business entities should be stored as strongly typed objects.
        """

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve runtime metadata.
        """

        return self.metadata.get(key, default)

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def has_parsed_document(self) -> bool:
        """
        Returns True if parsing has completed.
        """

        return self.parsed_document is not None

    @property
    def has_parsing_metadata(self) -> bool:
        """
        Returns True if parsing metadata has been generated.
        """

        return self.parsing_metadata is not None

    @property
    def chunk_count(self) -> int:
        """
        Returns the number of generated chunks.
        """

        return len(self.chunks)

    @property
    def embedding_count(self) -> int:
        """
        Returns the number of generated embeddings.
        """

        return len(self.embeddings)

    @property
    def vector_count(self) -> int:
        """
        Returns the number of generated vectors.
        """

        return len(self.vectors)


__all__ = [
    "ProcessingContext",
]
