"""
Document chunking utilities.

Responsible only for splitting parsed documents into
overlapping chunks for downstream processing.
"""

from __future__ import annotations

from backend.document_processing.models import (
    Chunk,
    ParsedDocument,
)


class TextChunker:
    """
    Splits text into overlapping chunks.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        text: str,
    ) -> list[str]:
        """
        Split plain text into overlapping chunks.
        """

        if not text or not text.strip():
            return []

        text = text.strip()

        chunks: list[str] = []

        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(
                start + self.chunk_size,
                text_length,
            )

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == text_length:
                break

            start = end - self.chunk_overlap

        return chunks

    def chunk_document(
        self,
        document: ParsedDocument,
    ) -> list[Chunk]:
        """
        Split a parsed document into Chunk objects.
        """

        chunks: list[Chunk] = []

        chunk_number = 1

        for page in document.pages:
            page_chunks = self.chunk(page.text)

            character_start = 0

            for text in page_chunks:
                character_end = character_start + len(text)

                chunks.append(
                    Chunk(
                        chunk_number=chunk_number,
                        page_number=page.page_number,
                        text=text,
                        character_start=character_start,
                        character_end=character_end,
                        token_count=None,
                    )
                )

                chunk_number += 1

                character_start = character_end - self.chunk_overlap

                if character_start < 0:
                    character_start = 0

        return chunks


__all__ = [
    "TextChunker",
]
