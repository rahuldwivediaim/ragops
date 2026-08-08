"""
Parsed Page Model

Represents a single parsed page extracted from a document.

Every document parser (PDF, DOCX, TXT, Markdown, etc.)
must produce ParsedPage objects so downstream services
(chunking, embeddings, retrieval) remain parser-agnostic.

Author: RAGOps
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ParsedPage:
    """
    Represents one parsed page.

    Attributes
    ----------
    page_number
        1-based page number.

    text
        Extracted text.

    metadata
        Optional parser-specific metadata.
    """

    page_number: int

    text: str

    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        """
        True if page contains no useful text.
        """

        return not self.text.strip()

    @property
    def character_count(self) -> int:
        """
        Number of characters in the page.
        """

        return len(self.text)

    @property
    def word_count(self) -> int:
        """
        Number of words in the page.
        """

        return len(self.text.split())

    @property
    def has_text(self) -> bool:
        """
        Returns True if the page contains text.
        """

        return not self.is_empty

    @property
    def line_count(self) -> int:
        """
        Returns the number of text lines.
        """

        return len([line for line in self.text.splitlines() if line.strip()])

    def __repr__(self) -> str:
        return (
            f"ParsedPage("
            f"page_number={self.page_number}, "
            f"characters={self.character_count}, "
            f"words={self.word_count})"
        )
