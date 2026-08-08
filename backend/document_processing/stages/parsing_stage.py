"""
File:
    backend/document_processing/stages/parsing_stage.py

Purpose:
    Parse a document using the appropriate parser.

Responsibilities

- Select the correct parser.
- Parse the document.
- Populate ProcessingContext.parsed_document.
- Populate ProcessingContext.parsing_metadata.

Persistence is intentionally handled outside this stage.
"""

from __future__ import annotations

from backend.document_processing.parsers.parser_factory import ParserFactory
from backend.document_processing.pipeline import (
    ProcessingContext,
    ProcessingStage,
)
from backend.models.document_parsing_metadata import (
    DocumentParsingMetadata,
)


class ParsingStage(ProcessingStage):
    """
    Parses the source document.
    """

    @property
    def name(self) -> str:
        return "Parsing"

    def execute(
        self,
        context: ProcessingContext,
    ) -> None:
        """
        Parse the source document.
        """

        parser = ParserFactory.create(context.source_file)

        parsed_document = parser.parse(context.source_file)

        context.parsed_document = parsed_document

        context.parsing_metadata = DocumentParsingMetadata(
            document_version_id=context.document_version_id,
            parser_name=parser.__class__.__name__,
            page_count=len(parsed_document.pages),
            word_count=parsed_document.word_count,
        )


__all__ = [
    "ParsingStage",
]
