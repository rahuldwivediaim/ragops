"""
Service layer for tenant management.

Tenant is the root ownership boundary of the RAG Framework.
"""

from __future__ import annotations

from uuid import UUID

from backend.models.tenant import Tenant
from backend.repositories.tenant_repository import TenantRepository
from backend.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    """Business service for Tenant operations."""

    def __init__(
        self,
        repository: TenantRepository,
    ) -> None:
        self._repository = repository

    def create(
        self,
        request: TenantCreate,
    ) -> Tenant:
        """
        Create a new tenant.

        Tenant codes must be unique.
        """

        existing = self._repository.get_by_code(
            request.code,
        )

        if existing is not None:
            raise ValueError(
                f"Tenant with code '{request.code}' already exists."
            )

        tenant = Tenant(
            code=request.code,
            name=request.name,
            description=request.description,
        )

        return self._repository.create(tenant)

    def get_by_id(
        self,
        tenant_id: UUID,
    ) -> Tenant:
        """Return a tenant by ID or raise ValueError."""

        return self._repository.get_by_id_or_raise(
            tenant_id,
        )

    def get_all(self) -> list[Tenant]:
        """Return all tenants."""

        return self._repository.get_all()

    def update(
        self,
        tenant_id: UUID,
        request: TenantUpdate,
    ) -> Tenant:
        """Update an existing tenant."""

        tenant = self._repository.get_by_id_or_raise(
            tenant_id,
        )

        if request.name is not None:
            tenant.name = request.name

        if request.description is not None:
            tenant.description = request.description

        if request.status is not None:
            tenant.status = request.status

        return self._repository.update(tenant)