"""
Domain service.

Purpose:
    Business logic for creating, updating and deleting persistent
    domains.

The service owns hierarchy validation. Database access is delegated
to DomainRepository.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.domain import Domain
from backend.models.enums import DomainStatus
from backend.repositories.domain_repository import DomainRepository


class DomainService:
    """
    Business logic for Domain management.

    Domain rules:
        - Domains are tenant-scoped.
        - Domain codes are unique within a tenant.
        - Domain names are unique within a tenant.
        - A parent must belong to the same tenant.
        - A domain cannot be its own parent.
        - Cycles are prohibited.
        - Maximum hierarchy depth is three levels.
    """

    MAX_DEPTH = 3

    def __init__(self, session: Session) -> None:
        self._repository = DomainRepository(session)

    def create(
        self,
        tenant_id: UUID,
        code: str,
        name: str,
        description: str | None = None,
        parent_id: UUID | None = None,
        status: DomainStatus = DomainStatus.ACTIVE,
    ) -> Domain:
        """Create a new domain after validating its hierarchy."""

        self._validate_unique_code(tenant_id, code)
        self._validate_unique_name(tenant_id, name)
        self._validate_parent(tenant_id, parent_id)

        if parent_id is not None:
            self._validate_parent_depth(tenant_id, parent_id)

        domain = Domain(
            tenant_id=tenant_id,
            parent_id=parent_id,
            code=code,
            name=name,
            description=description,
            status=status,
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
            "Domain not found.",
        )

    def get_by_code(
        self,
        tenant_id: UUID,
        code: str,
    ) -> Domain:
        """Return a domain by tenant-scoped business code."""

        domain = self._repository.get_by_code(tenant_id, code)

        if domain is None:
            raise ValueError(
                f"Domain with code '{code}' not found.",
            )

        return domain

    def get_all(
        self,
        tenant_id: UUID,
    ) -> list[Domain]:
        """Return all domains for a tenant."""

        return self._repository.get_all_ordered(tenant_id)

    def get_active(
        self,
        tenant_id: UUID,
    ) -> list[Domain]:
        """Return all active domains for a tenant."""

        return self._repository.get_active(tenant_id)

    def get_children(
        self,
        tenant_id: UUID,
        parent_id: UUID,
    ) -> list[Domain]:
        """Return direct children of a tenant-scoped domain."""

        self.get_by_id(tenant_id, parent_id)

        return self._repository.get_children(
            tenant_id,
            parent_id,
        )

    def update(
        self,
        tenant_id: UUID,
        domain_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        parent_id: UUID | None = None,
        status: DomainStatus | None = None,
    ) -> Domain:
        """Update a domain while preserving hierarchy invariants."""

        domain = self.get_by_id(
            tenant_id,
            domain_id,
        )

        if name is not None and name != domain.name:
            self._validate_unique_name(
                tenant_id,
                name,
                exclude_domain_id=domain_id,
            )
            domain.name = name

        if description is not None:
            domain.description = description

        if parent_id != domain.parent_id:
            self._validate_parent(
                tenant_id,
                parent_id,
                domain_id=domain_id,
            )

            if parent_id is not None:
                self._validate_parent_depth(
                    tenant_id,
                    parent_id,
                    moving_domain_id=domain_id,
                )

            domain.parent_id = parent_id

        if status is not None:
            domain.status = status

        return self._repository.update(domain)

    def activate(
        self,
        tenant_id: UUID,
        domain_id: UUID,
    ) -> Domain:
        """Activate a domain."""

        domain = self.get_by_id(tenant_id, domain_id)
        domain.status = DomainStatus.ACTIVE

        return self._repository.update(domain)

    def deactivate(
        self,
        tenant_id: UUID,
        domain_id: UUID,
    ) -> Domain:
        """Deactivate a domain."""

        domain = self.get_by_id(tenant_id, domain_id)
        domain.status = DomainStatus.INACTIVE

        return self._repository.update(domain)

    def delete(
        self,
        tenant_id: UUID,
        domain_id: UUID,
    ) -> None:
        """Delete a tenant-scoped domain."""

        domain = self.get_by_id(
            tenant_id,
            domain_id,
        )

        children = self._repository.get_children(
            tenant_id,
            domain.id,
        )

        if children:
            raise ValueError(
                f"Domain '{domain.code}' cannot be deleted because it "
                "has child domains.",
            )

        self._repository.delete(domain)

    def _validate_unique_code(
        self,
        tenant_id: UUID,
        code: str,
    ) -> None:
        """Validate tenant-scoped domain code uniqueness."""

        if self._repository.exists_by_code(
            tenant_id,
            code,
        ):
            raise ValueError(
                f"Domain code '{code}' already exists.",
            )

    def _validate_unique_name(
        self,
        tenant_id: UUID,
        name: str,
        exclude_domain_id: UUID | None = None,
    ) -> None:
        """Validate tenant-scoped domain name uniqueness."""

        existing = self._repository.get_by_name(
            tenant_id,
            name,
        )

        if existing is not None and existing.id != exclude_domain_id:
            raise ValueError(
                f"Domain name '{name}' already exists.",
            )

    def _validate_parent(
        self,
        tenant_id: UUID,
        parent_id: UUID | None,
        domain_id: UUID | None = None,
    ) -> None:
        """Validate that a parent is valid for the tenant and domain."""

        if parent_id is None:
            return

        if domain_id is not None and parent_id == domain_id:
            raise ValueError(
                "A domain cannot be its own parent.",
            )

        parent = self._repository.get_by_id(
            tenant_id,
            parent_id,
        )

        if parent is None:
            raise ValueError(
                f"Parent domain '{parent_id}' does not exist within the tenant.",
            )

        if domain_id is not None and self._is_descendant(
            tenant_id,
            parent_id,
            domain_id,
        ):
            raise ValueError(
                "The selected parent would create a domain hierarchy cycle.",
            )

    def _validate_parent_depth(
        self,
        tenant_id: UUID,
        parent_id: UUID,
        moving_domain_id: UUID | None = None,
    ) -> None:
        """Ensure the resulting hierarchy does not exceed MAX_DEPTH."""

        depth = 1
        current_id: UUID | None = parent_id
        visited: set[UUID] = set()

        while current_id is not None:
            if current_id in visited:
                raise ValueError(
                    "Domain hierarchy contains a cycle.",
                )

            visited.add(current_id)

            if moving_domain_id is not None and current_id == moving_domain_id:
                raise ValueError(
                    "The selected parent would create a domain hierarchy cycle.",
                )

            current = self._repository.get_by_id(
                tenant_id,
                current_id,
            )

            if current is None:
                raise ValueError(
                    f"Parent domain '{current_id}' does not exist within the tenant.",
                )

            if depth >= self.MAX_DEPTH:
                raise ValueError(
                    "Domain hierarchy exceeds the maximum "
                    f"domain hierarchy depth of {self.MAX_DEPTH}.",
                )

            current_id = current.parent_id
            depth += 1

    def _is_descendant(
        self,
        tenant_id: UUID,
        candidate_id: UUID,
        ancestor_id: UUID,
    ) -> bool:
        """Return whether candidate_id is below ancestor_id."""

        current_id: UUID | None = candidate_id
        visited: set[UUID] = set()

        while current_id is not None:
            if current_id in visited:
                return False

            visited.add(current_id)

            current = self._repository.get_by_id(
                tenant_id,
                current_id,
            )

            if current is None:
                return False

            if current.parent_id == ancestor_id:
                return True

            current_id = current.parent_id

        return False
