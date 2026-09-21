"""
Persistent Domain registry.

The registry is a read/query facade over persisted Domains.

Domain mutations belong to DomainService.
Database access belongs to DomainRepository.
The registry does not maintain an independent in-memory source of truth.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.domain import Domain
from backend.models.enums import DomainStatus
from backend.repositories.domain_repository import DomainRepository


class DomainRegistry:
    """
    Read-only registry for tenant-scoped persisted Domains.

    The registry provides hierarchy-oriented queries while delegating
    persistence access to DomainRepository.

    Domain creation, update and deletion are intentionally not supported
    here. Those operations belong to DomainService.
    """

    MAX_DEPTH = 3

    def __init__(
        self,
        session: Session,
        tenant_id: UUID,
    ) -> None:
        """
        Initialize a registry for one tenant.

        Parameters
        ----------
        session:
            SQLAlchemy session used for repository access.

        tenant_id:
            Tenant whose domains this registry exposes.
        """

        self._repository = DomainRepository(session)
        self._tenant_id = tenant_id

    def get(
        self,
        domain_id: UUID,
    ) -> Domain:
        """
        Return a domain by ID.

        Raises
        ------
        KeyError
            If the domain does not exist within the tenant.
        """

        domain = self._repository.get_by_id(
            self._tenant_id,
            domain_id,
        )

        if domain is None:
            raise KeyError(
                f"Domain '{domain_id}' is not registered.",
            )

        return domain

    def exists(
        self,
        domain_id: UUID,
    ) -> bool:
        """Return whether a domain exists within the tenant."""

        return (
            self._repository.get_by_id(
                self._tenant_id,
                domain_id,
            )
            is not None
        )

    def list_all(self) -> list[Domain]:
        """Return all domains for the tenant."""

        return self._repository.get_all_ordered(
            self._tenant_id,
        )

    def list_enabled(self) -> list[Domain]:
        """
        Return domains that are effectively enabled.

        A domain is effectively enabled only when the domain itself
        and every ancestor in its hierarchy are active.
        """

        domains = self._repository.get_active(
            self._tenant_id,
        )

        return [domain for domain in domains if self._is_effectively_enabled(domain.id)]

    def list_children(
        self,
        domain_id: UUID,
        *,
        enabled_only: bool = False,
    ) -> list[Domain]:
        """Return direct children of a domain."""

        self.get(domain_id)

        children = self._repository.get_children(
            self._tenant_id,
            domain_id,
        )

        if enabled_only:
            children = [
                domain for domain in children if self._is_effectively_enabled(domain.id)
            ]

        return children

    def list_descendants(
        self,
        domain_id: UUID,
        *,
        include_self: bool = False,
        enabled_only: bool = False,
    ) -> list[Domain]:
        """
        Return all descendants using breadth-first traversal.

        Children are returned in repository ordering.
        """

        self.get(domain_id)

        descendants: list[Domain] = []
        current_ids = [domain_id]

        while current_ids:
            next_ids: list[UUID] = []

            for current_id in current_ids:
                children = self.list_children(
                    current_id,
                    enabled_only=enabled_only,
                )

                descendants.extend(children)
                next_ids.extend(child.id for child in children)

            current_ids = next_ids

        if include_self:
            domain = self.get(domain_id)

            if not enabled_only or self._is_effectively_enabled(domain_id):
                return [domain, *descendants]

        return descendants

    def get_path(
        self,
        domain_id: UUID,
    ) -> tuple[Domain, ...]:
        """
        Return the hierarchy path from root to the requested domain.

        Example:

            HR -> Payroll -> Tax
        """

        current = self.get(domain_id)
        path: list[Domain] = [current]
        visited: set[UUID] = set()

        while current.parent_id is not None:
            if current.id in visited:
                raise ValueError(
                    "Domain hierarchy contains a cycle.",
                )

            visited.add(current.id)

            current = self.get(current.parent_id)
            path.append(current)

        path.reverse()

        return tuple(path)

    def get_path_ids(
        self,
        domain_id: UUID,
    ) -> tuple[UUID, ...]:
        """Return domain IDs from root to the requested domain."""

        return tuple(domain.id for domain in self.get_path(domain_id))

    def get_depth(
        self,
        domain_id: UUID,
    ) -> int:
        """
        Return the one-based hierarchy depth.

        Root domain = 1.
        Child domain = 2.
        Grandchild domain = 3.
        """

        return len(
            self.get_path(domain_id),
        )

    def is_descendant(
        self,
        domain_id: UUID,
        ancestor_id: UUID,
    ) -> bool:
        """
        Return whether domain_id is a descendant of ancestor_id.

        A domain is not considered a descendant of itself.
        """

        self.get(domain_id)
        self.get(ancestor_id)

        current = self.get(domain_id)
        visited: set[UUID] = set()

        while current.parent_id is not None:
            if current.id in visited:
                raise ValueError(
                    "Domain hierarchy contains a cycle.",
                )

            visited.add(current.id)

            if current.parent_id == ancestor_id:
                return True

            current = self.get(current.parent_id)

        return False

    def _is_effectively_enabled(
        self,
        domain_id: UUID,
    ) -> bool:
        """
        Return whether a domain and all its ancestors are active.
        """

        current = self.get(domain_id)
        visited: set[UUID] = set()

        while True:
            if current.id in visited:
                raise ValueError(
                    "Domain hierarchy contains a cycle.",
                )

            visited.add(current.id)

            if current.status is not DomainStatus.ACTIVE:
                return False

            if current.parent_id is None:
                return True

            current = self.get(current.parent_id)


__all__ = [
    "DomainRegistry",
]
