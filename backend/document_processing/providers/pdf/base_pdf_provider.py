"""
Base PDF Provider.

Defines the contract implemented by every PDF provider.

Author: RAGOps
"""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path

from backend.common.providers import (
    BaseProvider,
)
from backend.document_processing.models.parsed_document import (
    ParsedDocument,
)


class BasePdfProvider(BaseProvider):
    """
    Base class for all PDF providers.
    """

    @abstractmethod
    def parse(
        self,
        file_path: Path,
    ) -> ParsedDocument:
        """
        Parse a PDF document.
        """
