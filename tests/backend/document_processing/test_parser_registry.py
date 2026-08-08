"""
Tests for the parser registry.
"""

from backend.document_processing.parser_registry import (
    register_parsers,
)
from backend.document_processing.parsers.parser_factory import (
    ParserFactory,
)


def test_register_parsers() -> None:
    ParserFactory.clear()

    register_parsers()

    registered = ParserFactory.registered_parsers()

    assert "Text Parser" in registered
    assert "Markdown Parser" in registered
    assert "PDF Parser" in registered
