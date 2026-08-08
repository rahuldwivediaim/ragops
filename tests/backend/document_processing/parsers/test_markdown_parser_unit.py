"""
Tests for MarkdownParser.
"""

from pathlib import Path

from backend.document_processing.enums import DocumentFormat
from backend.document_processing.parsers.markdown_parser import (
    MarkdownParser,
)


def test_markdown_parser() -> None:
    """
    Verify that a Markdown file can be parsed.
    """

    sample_file = Path("samples/markdown/sample.md")

    assert sample_file.exists()

    parser = MarkdownParser()

    document = parser.parse(sample_file)

    assert document.filename == "sample.md"

    assert document.document_type == DocumentFormat.MARKDOWN

    assert document.page_count == 1

    assert len(document.pages) == 1

    assert document.word_count > 0

    assert not document.is_empty
