"""
File:
    backend/database/repositories/document_parsing_metadata_repository.py

Purpose:
    Repository for DocumentParsingMetadata entity.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, select

from backend.models.document_parsing_metadata import (
    DocumentParsingMetadata,
)
from backend.repositories.base_repository import BaseRepository


class DocumentParsingMetadataRepository(
    BaseRepository[DocumentParsingMetadata],
):
    """
    Repository for DocumentParsingMetadata.
    """

    def __init__(
        self,
        session,
    ) -> None:
        super().__init__(
            session=session,
            model=DocumentParsingMetadata,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_by_document_version(
        self,
        document_version_id: UUID,
    ) -> DocumentParsingMetadata | None:
        """
        Return parsing metadata for a document version.
        """

        statement: Select[tuple[DocumentParsingMetadata]] = (
            select(DocumentParsingMetadata)
            .where(DocumentParsingMetadata.document_version_id == document_version_id)
            .limit(1)
        )

        return self._session.scalar(statement)

    def exists(
        self,
        document_version_id: UUID,
    ) -> bool:
        """
        Return True if parsing metadata already exists.
        """

        return self.get_by_document_version(document_version_id) is not None


__all__ = [
    "DocumentParsingMetadataRepository",
]
