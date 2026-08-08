"""
Parser Factory

Creates the appropriate parser implementation based on the
uploaded document type.

The factory is intentionally registry-based rather than using
large if/else statements. This makes the parser framework
extensible without modifying existing code.

Author: RAGOps
"""

from __future__ import annotations

from pathlib import Path

from backend.document_processing.parsers.base_parser import BaseParser


class ParserFactory:
    """
    Factory responsible for creating document parsers.

    Parsers register themselves with the factory.
    """

    _parsers: list[BaseParser] = []

    @classmethod
    def register(
        cls,
        parser: BaseParser,
    ) -> None:
        """
        Register a parser implementation.

        Parameters
        ----------
        parser
            Parser instance.
        """

        if any(existing.parser_name == parser.parser_name for existing in cls._parsers):
            raise ValueError(f"Parser '{parser.parser_name}' is already registered.")

        cls._parsers.append(parser)

    @classmethod
    def create(
        cls,
        file_path: Path,
    ) -> BaseParser:
        """
        Return the parser capable of handling the file.

        Raises
        ------
        ValueError
            If no parser supports the supplied file.
        """

        for parser in cls._parsers:
            if parser.supports(file_path):
                return parser

        raise ValueError(f"No parser registered for '{file_path.suffix}'.")

    @classmethod
    def registered_parsers(
        cls,
    ) -> tuple[str, ...]:
        """
        Return registered parser names.
        """

        return tuple(parser.parser_name for parser in cls._parsers)

    @classmethod
    def parser_count(
        cls,
    ) -> int:
        """
        Return the number of registered parsers.
        """

        return len(cls._parsers)

    @classmethod
    def clear(
        cls,
    ) -> None:
        """
        Remove all registered parsers.

        Mainly used by unit tests.
        """

        cls._parsers.clear()
