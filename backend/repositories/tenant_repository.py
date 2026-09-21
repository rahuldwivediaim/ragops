"""
Repository for tenant persistence.

Tenant is the root ownership boundary for the RAG Framework.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.tenant import Tenant
from backend.repositories.base_repository import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Repository for Tenant entities."""

    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            model=Tenant,
        )

    def get_by_code(
        self,
        code: str,
    ) -> Tenant | None:
        """Return a tenant by its unique code."""

        statement = select(Tenant).where(
            Tenant.code == code,
        )

        return self._session.scalars(
            statement,
        ).first()

    def get_by_id_or_raise(
        self,
        tenant_id: UUID,
        message: str | None = None,
    ) -> Tenant:
        """
        Return a tenant by ID or raise ValueError.
        """

        return super().get_by_id_or_raise(
            tenant_id,
            message or f"Tenant not found: {tenant_id}",
        )