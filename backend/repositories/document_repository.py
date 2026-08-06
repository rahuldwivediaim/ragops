"""
File:
    backend/database/repositories/document_repository.py

Purpose:
    Repository for Document entity.

Description:
    Extends BaseRepository with document-specific queries.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, select

from backend.models.document import Document
from backend.models.enums import DocumentStatus

from .base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document."""

    def __init__(self, session) -> None:
        super().__init__(session=session, model=Document)

    def get_by_title(
        self,
        knowledge_base_id: UUID,
        title: str,
    ) -> Document | None:
        """Return a document by title within a knowledge base."""

        statement: Select[tuple[Document]] = (
            select(Document)
            .where(Document.knowledge_base_id == knowledge_base_id)
            .where(Document.title == title)
        )

        return self._session.scalar(statement)

    def exists_by_title(
        self,
        knowledge_base_id: UUID,
        title: str,
    ) -> bool:
        """Check whether a document title already exists."""

        return (
            self.get_by_title(
                knowledge_base_id=knowledge_base_id,
                title=title,
            )
            is not None
        )

    def get_by_status(
        self,
        status: DocumentStatus,
    ) -> list[Document]:
        """Return all documents with the given status."""

        statement: Select[tuple[Document]] = (
            select(Document)
            .where(Document.status == status)
            .order_by(Document.created_at.desc())
        )

        return list(self._session.scalars(statement).all())

    def get_by_knowledge_base(
        self,
        knowledge_base_id: UUID,
    ) -> list[Document]:
        """Return all documents for a knowledge base."""

        statement: Select[tuple[Document]] = (
            select(Document)
            .where(Document.knowledge_base_id == knowledge_base_id)
            .order_by(Document.created_at.desc())
        )

        return list(self._session.scalars(statement).all())

    def search(
        self,
        knowledge_base_id: UUID,
        search_text: str,
    ) -> list[Document]:
        """Search documents by title."""

        statement: Select[tuple[Document]] = (
            select(Document)
            .where(Document.knowledge_base_id == knowledge_base_id)
            .where(Document.title.ilike(f"%{search_text}%"))
            .order_by(Document.created_at.desc())
        )

        return list(self._session.scalars(statement).all())
