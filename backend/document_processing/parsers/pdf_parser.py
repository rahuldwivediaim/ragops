"""
PDF Parser.

Parses PDF documents using a configured PDF provider.

Author: RAGOps
"""

from __future__ import annotations

from pathlib import Path

from backend.document_processing.models.parsed_document import (
    ParsedDocument,
)
from backend.document_processing.parsers.base_parser import (
    BaseParser,
)
from backend.document_processing.providers.pdf.base_pdf_provider import (
    BasePdfProvider,
)


class PdfParser(BaseParser):
    """
    Parser for PDF documents.
    """

    def __init__(
        self,
        provider: BasePdfProvider,
    ) -> None:
        self._provider = provider

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        """
        Supported file extensions.
        """
        return (".pdf",)

    @property
    def parser_name(self) -> str:
        """
        Human-readable parser name.
        """
        return "PDF Parser"

    def parse(
        self,
        file_path: Path,
    ) -> ParsedDocument:
        """
        Parse a PDF document.
        """
        return self._provider.parse(file_path)
