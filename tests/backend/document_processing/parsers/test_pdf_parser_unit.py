"""
Tests for PdfParser.
"""

from pathlib import Path

from backend.document_processing.enums import DocumentFormat
from backend.document_processing.parsers.pdf_parser import (
    PdfParser,
)
from backend.document_processing.providers.pdf.pymupdf_provider import (
    PyMuPDFProvider,
)


def test_pdf_parser() -> None:
    """
    Verify that PdfParser parses a PDF successfully.
    """

    sample_pdf = Path("samples/HR Policy – Employee Handbook.pdf")

    assert sample_pdf.exists()

    parser = PdfParser(
        provider=PyMuPDFProvider(),
    )

    document = parser.parse(sample_pdf)

    assert document.document_type == DocumentFormat.PDF

    assert document.page_count > 0

    assert len(document.pages) == document.page_count

    assert document.word_count > 0

    assert not document.is_empty
