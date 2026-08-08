"""
Parser Registry.

Registers all document parsers supported by RAGOps.

Author: RAGOps
"""

from __future__ import annotations

from backend.document_processing.parsers.markdown_parser import (
    MarkdownParser,
)
from backend.document_processing.parsers.parser_factory import (
    ParserFactory,
)
from backend.document_processing.parsers.pdf_parser import (
    PdfParser,
)
from backend.document_processing.parsers.text_parser import (
    TextParser,
)
from backend.document_processing.providers.pdf.pymupdf_provider import (
    PyMuPDFProvider,
)


def register_parsers() -> None:
    """
    Register all document parsers.
    """

    ParserFactory.clear()

    ParserFactory.register(
        TextParser(),
    )

    ParserFactory.register(
        MarkdownParser(),
    )

    ParserFactory.register(
        PdfParser(
            provider=PyMuPDFProvider(),
        ),
    )
