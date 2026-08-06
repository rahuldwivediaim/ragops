"""
File:
    backend/database/repositories/document_version_repository.py

Purpose:
    Repository for DocumentVersion entity.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select

from backend.repositories.base_repository import BaseRepository
from backend.models.document_version import DocumentVersion


class DocumentVersionRepository(BaseRepository[DocumentVersion]):
    """Repository for DocumentVersion."""

    def __init__(self, session) -> None:
        super().__init__(
            session=session,
            model=DocumentVersion,
        )

    def get_by_document(
        self,
        document_id: UUID,
    ) -> list[DocumentVersion]:
        """Return all versions for a document."""

        statement: Select[tuple[DocumentVersion]] = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )

        return list(self._session.scalars(statement).all())

    def get_latest(
        self,
        document_id: UUID,
    ) -> DocumentVersion | None:
        """Return the latest version for a document."""

        statement: Select[tuple[DocumentVersion]] = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .limit(1)
        )

        return self._session.scalar(statement)

    def get_by_version(
        self,
        document_id: UUID,
        version_number: int,
    ) -> DocumentVersion | None:
        """Return a specific document version."""

        statement: Select[tuple[DocumentVersion]] = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .where(DocumentVersion.version_number == version_number)
        )

        return self._session.scalar(statement)

    def get_next_version_number(
        self,
        document_id: UUID,
    ) -> int:
        """Return the next version number for a document."""

        statement = select(func.max(DocumentVersion.version_number)).where(
            DocumentVersion.document_id == document_id
        )

        current = self._session.scalar(statement)

        return 1 if current is None else current + 1

    def exists_by_hash(
        self,
        content_hash: str,
    ) -> bool:
        """Return True if the content hash already exists."""

        statement: Select[tuple[DocumentVersion]] = (
            select(DocumentVersion)
            .where(DocumentVersion.content_hash == content_hash)
            .limit(1)
        )

        return self._session.scalar(statement) is not None

    def get_by_hash(
        self,
        content_hash: str,
    ) -> DocumentVersion | None:
        """Return a document version by content hash."""

        statement: Select[tuple[DocumentVersion]] = (
            select(DocumentVersion)
            .where(DocumentVersion.content_hash == content_hash)
            .limit(1)
        )

        return self._session.scalar(statement)
