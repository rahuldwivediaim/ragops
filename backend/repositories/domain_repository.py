"""
Domain repository.

Purpose:
    Repository for Domain database operations.

The repository keeps all Domain access tenant-scoped so that a Domain
from one tenant can never be accidentally resolved while operating
within another tenant.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.domain import Domain
from backend.models.enums import DomainStatus
from backend.repositories.base_repository import BaseRepository


class DomainRepository(BaseRepository[Domain]):
    """Repository for tenant-scoped Domain operations."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Domain)

    def get_by_id(
        self,
        tenant_id: UUID,
        domain_id: UUID,
    ) -> Domain | None:
        """Return a domain by ID within a tenant."""

        statement = select(Domain).where(
            Domain.tenant_id == tenant_id,
            Domain.id == domain_id,
        )

        return self._session.scalar(statement)

    def get_by_id_or_raise(
        self,
        tenant_id: UUID,
        domain_id: UUID,
        message: str | None = None,
    ) -> Domain:
        """Return a tenant-scoped domain or raise ValueError."""

        domain = self.get_by_id(
            tenant_id,
            domain_id,
        )

        if domain is None:
            raise ValueError(
                message or f"Domain '{domain_id}' not found.",
            )

        return domain

    def get_by_code(
        self,
        tenant_id: UUID,
        code: str,
    ) -> Domain | None:
        """Return a domain by code within a tenant."""

        statement = select(Domain).where(
            Domain.tenant_id == tenant_id,
            Domain.code == code,
        )

        return self._session.scalar(statement)

    def get_by_name(
        self,
        tenant_id: UUID,
        name: str,
    ) -> Domain | None:
        """Return a domain by name within a tenant."""

        statement = select(Domain).where(
            Domain.tenant_id == tenant_id,
            Domain.name == name,
        )

        return self._session.scalar(statement)

    def exists_by_code(
        self,
        tenant_id: UUID,
        code: str,
    ) -> bool:
        """Check whether a domain code exists within a tenant."""

        statement = (
            select(func.count())
            .select_from(Domain)
            .where(
                Domain.tenant_id == tenant_id,
                Domain.code == code,
            )
        )

        return (self._session.scalar(statement) or 0) > 0

    def exists_by_name(
        self,
        tenant_id: UUID,
        name: str,
    ) -> bool:
        """Check whether a domain name exists within a tenant."""

        statement = (
            select(func.count())
            .select_from(Domain)
            .where(
                Domain.tenant_id == tenant_id,
                Domain.name == name,
            )
        )

        return (self._session.scalar(statement) or 0) > 0

    def get_root_domains(
        self,
        tenant_id: UUID,
    ) -> list[Domain]:
        """Return root domains for a tenant."""

        statement = (
            select(Domain)
            .where(
                Domain.tenant_id == tenant_id,
                Domain.parent_id.is_(None),
            )
            .order_by(Domain.name)
        )

        return list(self._session.scalars(statement).all())

    def get_children(
        self,
        tenant_id: UUID,
        parent_id: UUID,
    ) -> list[Domain]:
        """Return direct child domains for a tenant."""

        statement = (
            select(Domain)
            .where(
                Domain.tenant_id == tenant_id,
                Domain.parent_id == parent_id,
            )
            .order_by(Domain.name)
        )

        return list(self._session.scalars(statement).all())

    def get_active(
        self,
        tenant_id: UUID,
    ) -> list[Domain]:
        """Return all active domains for a tenant."""

        statement = (
            select(Domain)
            .where(
                Domain.tenant_id == tenant_id,
                Domain.status == DomainStatus.ACTIVE,
            )
            .order_by(Domain.name)
        )

        return list(self._session.scalars(statement).all())

    def get_all_ordered(
        self,
        tenant_id: UUID,
    ) -> list[Domain]:
        """Return all domains for a tenant ordered by name."""

        statement = (
            select(Domain).where(Domain.tenant_id == tenant_id).order_by(Domain.name)
        )

        return list(self._session.scalars(statement).all())
