"""
File:
    backend/repositories/knowledge_base_repository.py

Purpose:
    Repository for Knowledge Base database operations.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.enums import KnowledgeBaseStatus
from backend.models.knowledge_base import KnowledgeBase
from backend.repositories.base_repository import BaseRepository


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    """Repository for KnowledgeBase."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, KnowledgeBase)

    def get_by_code(self, code: str) -> KnowledgeBase | None:
        """Return a knowledge base by its code."""

        statement = select(KnowledgeBase).where(
            KnowledgeBase.code == code,
        )

        return self._session.scalar(statement)

    def get_by_name(self, name: str) -> KnowledgeBase | None:
        """Return a knowledge base by its name."""

        statement = select(KnowledgeBase).where(
            KnowledgeBase.name == name,
        )

        return self._session.scalar(statement)

    def exists_by_code(self, code: str) -> bool:
        """Check whether a knowledge base code already exists."""

        statement = (
            select(func.count())
            .select_from(KnowledgeBase)
            .where(KnowledgeBase.code == code)
        )

        return (self._session.scalar(statement) or 0) > 0

    def exists_by_name(self, name: str) -> bool:
        """Check whether a knowledge base name already exists."""

        statement = (
            select(func.count())
            .select_from(KnowledgeBase)
            .where(KnowledgeBase.name == name)
        )

        return (self._session.scalar(statement) or 0) > 0

    def get_active(self) -> list[KnowledgeBase]:
        """Return all active knowledge bases."""

        statement = (
            select(KnowledgeBase)
            .where(
                KnowledgeBase.status == KnowledgeBaseStatus.ACTIVE,
            )
            .order_by(KnowledgeBase.name)
        )

        return list(self._session.scalars(statement).all())

    def get_all_ordered(self) -> list[KnowledgeBase]:
        """Return all knowledge bases ordered by name."""

        statement = select(KnowledgeBase).order_by(KnowledgeBase.name)

        return list(self._session.scalars(statement).all())
