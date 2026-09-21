"""
File:
    backend/services/knowledge_base_service.py

Purpose:
    Business logic for Knowledge Base management.

A Knowledge Base belongs to exactly one Tenant and one Domain.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.knowledge_base import KnowledgeBase
from backend.repositories.domain_repository import DomainRepository
from backend.repositories.knowledge_base_repository import (
    KnowledgeBaseRepository,
)
from backend.repositories.tenant_repository import TenantRepository
from backend.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
)


class KnowledgeBaseService:
    """Business logic for Knowledge Base operations."""

    def __init__(self, session: Session) -> None:
        self._session = session

        self._repository = KnowledgeBaseRepository(
            session,
        )

        self._tenant_repository = TenantRepository(
            session,
        )

        self._domain_repository = DomainRepository(
            session,
        )

    def create(
        self,
        request: KnowledgeBaseCreate,
    ) -> KnowledgeBase:
        """
        Create a Knowledge Base.

        Validates:

        1. Tenant exists.
        2. Domain exists within that tenant.
        3. Code is unique within the tenant.
        4. Name is unique within the tenant.
        """

        # ---------------------------------------------------------
        # 1. Validate tenant
        # ---------------------------------------------------------

        self._tenant_repository.get_by_id_or_raise(
            request.tenant_id,
            f"Tenant not found: {request.tenant_id}",
        )

        # ---------------------------------------------------------
        # 2. Validate domain belongs to tenant
        # ---------------------------------------------------------

        self._domain_repository.get_by_id_or_raise(
            request.tenant_id,
            request.domain_id,
            (
                f"Domain '{request.domain_id}' "
                f"does not exist for tenant "
                f"'{request.tenant_id}'."
            ),
        )

        # ---------------------------------------------------------
        # 3. Validate code uniqueness within tenant
        # ---------------------------------------------------------

        if self._repository.exists_by_code(
            request.tenant_id,
            request.code,
        ):
            raise ValueError(
                f"Knowledge Base code '{request.code}' "
                f"already exists for this tenant."
            )

        # ---------------------------------------------------------
        # 4. Validate name uniqueness within tenant
        # ---------------------------------------------------------

        if self._repository.exists_by_name(
            request.tenant_id,
            request.name,
        ):
            raise ValueError(
                f"Knowledge Base name '{request.name}' "
                f"already exists for this tenant."
            )

        # ---------------------------------------------------------
        # 5. Create Knowledge Base
        # ---------------------------------------------------------

        knowledge_base = KnowledgeBase(
            tenant_id=request.tenant_id,
            domain_id=request.domain_id,
            code=request.code,
            name=request.name,
            description=request.description,
            owner=request.owner,
            default_language=request.default_language,
        )

        return self._repository.create(
            knowledge_base,
        )

    def get_by_id(
        self,
        knowledge_base_id: UUID,
    ) -> KnowledgeBase:
        """Return a Knowledge Base by ID."""

        return self._repository.get_by_id_or_raise(
            knowledge_base_id,
            "Knowledge Base not found.",
        )

    def get_all(self) -> list[KnowledgeBase]:
        """Return all Knowledge Bases."""

        return self._repository.get_all_ordered()

    def get_active(self) -> list[KnowledgeBase]:
        """Return all active Knowledge Bases."""

        return self._repository.get_active()

    def update(
        self,
        knowledge_base_id: UUID,
        request: KnowledgeBaseUpdate,
    ) -> KnowledgeBase:
        """Update an existing Knowledge Base."""

        knowledge_base = self._repository.get_by_id_or_raise(
            knowledge_base_id,
            "Knowledge Base not found.",
        )

        if (
            request.name is not None
            and request.name != knowledge_base.name
        ):
            if self._repository.exists_by_name(
                knowledge_base.tenant_id,
                request.name,
            ):
                raise ValueError(
                    f"Knowledge Base name '{request.name}' "
                    f"already exists for this tenant."
                )

            knowledge_base.name = request.name

        if request.description is not None:
            knowledge_base.description = request.description

        if request.owner is not None:
            knowledge_base.owner = request.owner

        if request.default_language is not None:
            knowledge_base.default_language = (
                request.default_language
            )

        if request.status is not None:
            knowledge_base.status = request.status

        return self._repository.update(
            knowledge_base,
        )

    def delete(
        self,
        knowledge_base_id: UUID,
    ) -> None:
        """Delete a Knowledge Base."""

        knowledge_base = self._repository.get_by_id_or_raise(
            knowledge_base_id,
            "Knowledge Base not found.",
        )

        self._repository.delete(
            knowledge_base,
        )