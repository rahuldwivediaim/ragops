"""
Base Parser

Defines the abstract interface implemented by every document parser.

All parsers must return a ParsedDocument regardless of the
underlying document type.

Author: RAGOps
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from backend.document_processing.models.parsed_document import (
    ParsedDocument,
)


class BaseParser(ABC):
    """
    Abstract base class for all document parsers.
    """

    @property
    @abstractmethod
    def supported_extensions(self) -> tuple[str, ...]:
        """
        Supported file extensions.

        Example
        -------
        (".pdf",)
        """

    @property
    @abstractmethod
    def parser_name(self) -> str:
        """
        Human-readable parser name.
        """

    @abstractmethod
    def parse(
        self,
        file_path: Path,
    ) -> ParsedDocument:
        """
        Parse a document.

        Parameters
        ----------
        file_path
            Path to the document.

        Returns
        -------
        ParsedDocument
        """

    def supports(
        self,
        file_path: Path,
    ) -> bool:
        """
        Returns True if this parser supports the file.
        """

        return file_path.suffix.lower() in self.supported_extensions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(parser='{self.parser_name}')"
