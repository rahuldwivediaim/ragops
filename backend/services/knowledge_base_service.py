"""
File:
    backend/services/knowledge_base_service.py

Purpose:
    Business logic for Knowledge Base management.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.knowledge_base import KnowledgeBase
from backend.repositories.knowledge_base_repository import (
    KnowledgeBaseRepository,
)
from backend.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
)


class KnowledgeBaseService:
    """Business logic for Knowledge Base operations."""

    def __init__(self, session: Session) -> None:
        self._repository = KnowledgeBaseRepository(session)

    def create(
        self,
        request: KnowledgeBaseCreate,
    ) -> KnowledgeBase:
        if self._repository.exists_by_code(request.code):
            raise ValueError(f"Knowledge Base code '{request.code}' already exists.")

        if self._repository.exists_by_name(request.name):
            raise ValueError(f"Knowledge Base name '{request.name}' already exists.")

        knowledge_base = KnowledgeBase(
            code=request.code,
            name=request.name,
            description=request.description,
            owner=request.owner,
            default_language=request.default_language,
        )

        return self._repository.create(knowledge_base)

    def get_by_id(
        self,
        knowledge_base_id: UUID,
    ) -> KnowledgeBase:
        return self._repository.get_by_id_or_raise(
            knowledge_base_id,
            "Knowledge Base not found.",
        )

    def get_all(self) -> list[KnowledgeBase]:
        return self._repository.get_all_ordered()

    def get_active(self) -> list[KnowledgeBase]:
        return self._repository.get_active()

    def update(
        self,
        knowledge_base_id: UUID,
        request: KnowledgeBaseUpdate,
    ) -> KnowledgeBase:
        knowledge_base = self._repository.get_by_id_or_raise(
            knowledge_base_id,
            "Knowledge Base not found.",
        )

        if request.name is not None and request.name != knowledge_base.name:
            if self._repository.exists_by_name(request.name):
                raise ValueError(
                    f"Knowledge Base name '{request.name}' already exists."
                )

            knowledge_base.name = request.name

        if request.description is not None:
            knowledge_base.description = request.description

        if request.owner is not None:
            knowledge_base.owner = request.owner

        if request.default_language is not None:
            knowledge_base.default_language = request.default_language

        if request.status is not None:
            knowledge_base.status = request.status

        return self._repository.update(knowledge_base)

    def delete(
        self,
        knowledge_base_id: UUID,
    ) -> None:
        knowledge_base = self._repository.get_by_id_or_raise(
            knowledge_base_id,
            "Knowledge Base not found.",
        )

        self._repository.delete(knowledge_base)
