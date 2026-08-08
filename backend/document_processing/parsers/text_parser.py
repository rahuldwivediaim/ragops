"""
Text Parser

Parser implementation for plain text documents.

Author: RAGOps
"""

from __future__ import annotations

from pathlib import Path
from backend.document_processing.enums import DocumentFormat

from backend.document_processing.models.parsed_document import (
    ParsedDocument,
)
from backend.document_processing.models.parsed_page import (
    ParsedPage,
)
from backend.document_processing.parsers.base_parser import (
    BaseParser,
)


class TextParser(BaseParser):
    """
    Parser for plain text documents.
    """

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """
        Supported file extensions.
        """

        return (".txt",)

    @property
    def parser_name(self) -> str:
        """
        Parser name.
        """

        return "Text Parser"

    def parse(
        self,
        file_path: Path,
    ) -> ParsedDocument:
        """
        Parse a text file.
        """

        text = file_path.read_text(
            encoding="utf-8",
        )

        page = ParsedPage(
            page_number=1,
            text=text,
        )

        document = ParsedDocument(
            filename=file_path.name,
            document_type=DocumentFormat.TXT,
            page_count=1,
        )

        document.add_page(page)

        return document
