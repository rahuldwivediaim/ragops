"""
Service layer for tenant-scoped domain management.

Domains represent business classifications within a tenant and may
form a parent/child hierarchy.
"""

from __future__ import annotations

from uuid import UUID

from backend.models.domain import Domain
from backend.repositories.domain_repository import DomainRepository
from backend.schemas.domain import DomainCreate, DomainUpdate


class DomainService:
    """Business service for Domain operations."""

    def __init__(
        self,
        repository: DomainRepository,
    ) -> None:
        self._repository = repository

    def create(
        self,
        request: DomainCreate,
    ) -> Domain:
        """
        Create a new domain.

        Validates tenant-scoped uniqueness and, when supplied,
        validates that the parent belongs to the same tenant.
        """

        if self._repository.exists_by_code(
            request.tenant_id,
            request.code,
        ):
            raise ValueError(
                f"Domain with code '{request.code}' "
                f"already exists for this tenant."
            )

        if self._repository.exists_by_name(
            request.tenant_id,
            request.name,
        ):
            raise ValueError(
                f"Domain with name '{request.name}' "
                f"already exists for this tenant."
            )

        parent = None

        if request.parent_id is not None:
            parent = self._repository.get_by_id_or_raise(
                request.tenant_id,
                request.parent_id,
                (
                    f"Parent domain '{request.parent_id}' "
                    f"does not exist for tenant "
                    f"'{request.tenant_id}'."
                ),
            )

        domain = Domain(
            tenant_id=request.tenant_id,
            parent_id=parent.id if parent is not None else None,
            code=request.code,
            name=request.name,
            description=request.description,
        )

        return self._repository.create(domain)

    def get_by_id(
        self,
        tenant_id: UUID,
        domain_id: UUID,
    ) -> Domain:
        """Return a tenant-scoped domain."""

        return self._repository.get_by_id_or_raise(
            tenant_id,
            domain_id,
        )

    def get_all(
        self,
        tenant_id: UUID,
    ) -> list[Domain]:
        """Return all domains for a tenant."""

        return self._repository.get_all_ordered(
            tenant_id,
        )

    def get_roots(
        self,
        tenant_id: UUID,
    ) -> list[Domain]:
        """Return root domains for a tenant."""

        return self._repository.get_root_domains(
            tenant_id,
        )

    def get_children(
        self,
        tenant_id: UUID,
        parent_id: UUID,
    ) -> list[Domain]:
        """Return direct child domains."""

        # First ensure the parent belongs to this tenant.
        self._repository.get_by_id_or_raise(
            tenant_id,
            parent_id,
        )

        return self._repository.get_children(
            tenant_id,
            parent_id,
        )

    def get_active(
        self,
        tenant_id: UUID,
    ) -> list[Domain]:
        """Return all active domains for a tenant."""

        return self._repository.get_active(
            tenant_id,
        )

    def update(
        self,
        tenant_id: UUID,
        domain_id: UUID,
        request: DomainUpdate,
    ) -> Domain:
        """Update a tenant-scoped domain."""

        domain = self._repository.get_by_id_or_raise(
            tenant_id,
            domain_id,
        )

        if request.code is not None and request.code != domain.code:
            if self._repository.exists_by_code(
                tenant_id,
                request.code,
            ):
                raise ValueError(
                    f"Domain with code '{request.code}' "
                    f"already exists for this tenant."
                )

            domain.code = request.code

        if request.name is not None and request.name != domain.name:
            if self._repository.exists_by_name(
                tenant_id,
                request.name,
            ):
                raise ValueError(
                    f"Domain with name '{request.name}' "
                    f"already exists for this tenant."
                )

            domain.name = request.name

        if request.description is not None:
            domain.description = request.description

        if request.parent_id != domain.parent_id:
            if request.parent_id is None:
                domain.parent_id = None

            else:
                if request.parent_id == domain.id:
                    raise ValueError(
                        "A domain cannot be its own parent."
                    )

                parent = self._repository.get_by_id_or_raise(
                    tenant_id,
                    request.parent_id,
                    (
                        f"Parent domain '{request.parent_id}' "
                        f"does not exist for tenant "
                        f"'{tenant_id}'."
                    ),
                )

                domain.parent_id = parent.id

        if request.status is not None:
            domain.status = request.status

        return self._repository.update(domain)