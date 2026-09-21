"""
Tenant management API.

Tenant is the root ownership boundary for the RAG Framework.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.repositories.tenant_repository import TenantRepository
from backend.schemas.tenant import (
    TenantCreate,
    TenantResponse,
    TenantUpdate,
)
from backend.services.tenant_service import TenantService


router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)


def get_tenant_service(
    session: Annotated[Session, Depends(get_db)],
) -> TenantService:
    """Build the TenantService dependency."""

    repository = TenantRepository(
        session=session,
    )

    return TenantService(
        repository=repository,
    )


TenantServiceDependency = Annotated[
    TenantService,
    Depends(get_tenant_service),
]


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    request: TenantCreate,
    service: TenantServiceDependency,
) -> TenantResponse:
    """Create a new tenant."""

    try:
        tenant = service.create(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return TenantResponse.model_validate(tenant)


@router.get(
    "",
    response_model=list[TenantResponse],
)
def list_tenants(
    service: TenantServiceDependency,
) -> list[TenantResponse]:
    """Return all tenants."""

    tenants = service.get_all()

    return [
        TenantResponse.model_validate(tenant)
        for tenant in tenants
    ]


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
)
def get_tenant(
    tenant_id: UUID,
    service: TenantServiceDependency,
) -> TenantResponse:
    """Return a tenant by ID."""

    try:
        tenant = service.get_by_id(tenant_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return TenantResponse.model_validate(tenant)


@router.put(
    "/{tenant_id}",
    response_model=TenantResponse,
)
def update_tenant(
    tenant_id: UUID,
    request: TenantUpdate,
    service: TenantServiceDependency,
) -> TenantResponse:
    """Update a tenant."""

    try:
        tenant = service.update(
            tenant_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return TenantResponse.model_validate(tenant)