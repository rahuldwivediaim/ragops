"""
File:
    backend/repositories/knowledge_base_repository.py

Purpose:
    Repository for Knowledge Base database operations.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.enums import KnowledgeBaseStatus
from backend.models.knowledge_base import KnowledgeBase
from backend.repositories.base_repository import BaseRepository


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    """Repository for Knowledge Base database operations."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, KnowledgeBase)

    def get_by_code(
        self,
        tenant_id: UUID,
        code: str,
    ) -> KnowledgeBase | None:
        """Return a knowledge base by code within a tenant."""

        statement = select(KnowledgeBase).where(
            KnowledgeBase.tenant_id == tenant_id,
            KnowledgeBase.code == code,
        )

        return self._session.scalar(statement)

    def get_by_name(
        self,
        tenant_id: UUID,
        name: str,
    ) -> KnowledgeBase | None:
        """Return a knowledge base by name within a tenant."""

        statement = select(KnowledgeBase).where(
            KnowledgeBase.tenant_id == tenant_id,
            KnowledgeBase.name == name,
        )

        return self._session.scalar(statement)

    def exists_by_code(
        self,
        tenant_id: UUID,
        code: str,
    ) -> bool:
        """Check whether a knowledge base code exists within a tenant."""

        statement = (
            select(func.count())
            .select_from(KnowledgeBase)
            .where(
                KnowledgeBase.tenant_id == tenant_id,
                KnowledgeBase.code == code,
            )
        )

        return (self._session.scalar(statement) or 0) > 0

    def exists_by_name(
        self,
        tenant_id: UUID,
        name: str,
    ) -> bool:
        """Check whether a knowledge base name exists within a tenant."""

        statement = (
            select(func.count())
            .select_from(KnowledgeBase)
            .where(
                KnowledgeBase.tenant_id == tenant_id,
                KnowledgeBase.name == name,
            )
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

        statement = (
            select(KnowledgeBase)
            .order_by(KnowledgeBase.name)
        )

        return list(self._session.scalars(statement).all())