"""
Document parser registrations.

Importing this package registers the supported document parsers
with ParserFactory.
"""

from backend.document_processing.parsers.parser_factory import ParserFactory
from backend.document_processing.parsers.text_parser import TextParser
from backend.document_processing.parsers.markdown_parser import MarkdownParser


ParserFactory.register(TextParser())
ParserFactory.register(MarkdownParser())