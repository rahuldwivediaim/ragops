"""
Parsed Document Model

Represents the normalized output produced by every document parser.

Regardless of whether the source document is a PDF, DOCX, TXT,
Markdown, HTML, etc., the parser must return a ParsedDocument.

This abstraction allows downstream services such as chunking,
embedding generation and retrieval to remain independent of
individual parser implementations.

Author: RAGOps
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.document_processing.models.parsed_page import ParsedPage


@dataclass(slots=True)
class ParsedDocument:
    """
    Represents a parsed document.

    Attributes
    ----------
    filename
        Original file name.

    document_type
        Document type (PDF, DOCX, TXT, etc.).

    page_count
        Number of parsed pages.

    language
        Detected document language.

    metadata
        Parser-specific metadata.

    pages
        Parsed pages.
    """

    filename: str

    document_type: str

    page_count: int

    language: str = "unknown"

    metadata: dict[str, str] = field(default_factory=dict)

    pages: list[ParsedPage] = field(default_factory=list)

    @property
    def text(self) -> str:
        """
        Returns the complete document text.
        """

        return "\n\n".join(page.text for page in self.pages)

    @property
    def character_count(self) -> int:
        """
        Total number of characters.
        """

        return len(self.text)

    @property
    def word_count(self) -> int:
        """
        Total number of words.
        """

        return len(self.text.split())

    @property
    def has_pages(self) -> bool:
        """
        Returns True if the document contains at least one page.
        """

        return len(self.pages) > 0

    @property
    def is_empty(self) -> bool:
        """
        True if every page is empty.
        """

        return all(page.is_empty for page in self.pages)

    def add_page(
        self,
        page: ParsedPage,
    ) -> None:
        """
        Add a parsed page.
        """

        self.pages.append(page)
        self.page_count = len(self.pages)

    def page(
        self,
        page_number: int,
    ) -> ParsedPage:
        """
        Returns a page by page number.
        """

        for page in self.pages:
            if page.page_number == page_number:
                return page

        raise ValueError(f"Page {page_number} does not exist.")

    def __repr__(self) -> str:
        return (
            f"ParsedDocument("
            f"filename='{self.filename}', "
            f"pages={self.page_count}, "
            f"words={self.word_count})"
        )
