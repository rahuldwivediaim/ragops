"""
Tests for TextParser.
"""

from pathlib import Path

from backend.document_processing.parsers.text_parser import TextParser
from backend.document_processing.enums import DocumentFormat


def test_text_parser() -> None:
    """
    Verify that a text file can be parsed successfully.
    """

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists()

    parser = TextParser()

    document = parser.parse(sample_file)

    assert document.filename == "sample.txt"

    assert document.page_count == 1

    assert len(document.pages) == 1

    assert document.document_type == DocumentFormat.TXT

    assert document.word_count > 0

    assert not document.is_empty

    print()
    print("=" * 80)
    print(document)
    print("=" * 80)
    print(document.text)
    print("=" * 80)
