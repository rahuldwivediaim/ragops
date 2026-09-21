"""
Domain management API.

Domains are tenant-scoped and may form a parent/child hierarchy.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.repositories.domain_repository import DomainRepository
from backend.schemas.domain import (
    DomainCreate,
    DomainResponse,
    DomainUpdate,
)
from backend.services.domain_service import DomainService


router = APIRouter(
    prefix="/tenants/{tenant_id}/domains",
    tags=["Domains"],
)


def get_domain_service(
    session: Annotated[Session, Depends(get_db)],
) -> DomainService:
    """Build the DomainService dependency."""

    repository = DomainRepository(
        session=session,
    )

    return DomainService(
        repository=repository,
    )


DomainServiceDependency = Annotated[
    DomainService,
    Depends(get_domain_service),
]


@router.post(
    "",
    response_model=DomainResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_domain(
    tenant_id: UUID,
    request: DomainCreate,
    service: DomainServiceDependency,
) -> DomainResponse:
    """Create a domain for a tenant."""

    if request.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Tenant ID in request body does not match "
                "the tenant ID in the URL."
            ),
        )

    try:
        domain = service.create(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return DomainResponse.model_validate(domain)


@router.get(
    "",
    response_model=list[DomainResponse],
)
def list_domains(
    tenant_id: UUID,
    service: DomainServiceDependency,
) -> list[DomainResponse]:
    """Return all domains for a tenant."""

    domains = service.get_all(tenant_id)

    return [
        DomainResponse.model_validate(domain)
        for domain in domains
    ]


@router.get(
    "/roots",
    response_model=list[DomainResponse],
)
def list_root_domains(
    tenant_id: UUID,
    service: DomainServiceDependency,
) -> list[DomainResponse]:
    """Return root domains for a tenant."""

    domains = service.get_roots(tenant_id)

    return [
        DomainResponse.model_validate(domain)
        for domain in domains
    ]


@router.get(
    "/active",
    response_model=list[DomainResponse],
)
def list_active_domains(
    tenant_id: UUID,
    service: DomainServiceDependency,
) -> list[DomainResponse]:
    """Return active domains for a tenant."""

    domains = service.get_active(tenant_id)

    return [
        DomainResponse.model_validate(domain)
        for domain in domains
    ]


@router.get(
    "/{domain_id}/children",
    response_model=list[DomainResponse],
)
def list_child_domains(
    tenant_id: UUID,
    domain_id: UUID,
    service: DomainServiceDependency,
) -> list[DomainResponse]:
    """Return direct children of a domain."""

    try:
        domains = service.get_children(
            tenant_id,
            domain_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [
        DomainResponse.model_validate(domain)
        for domain in domains
    ]


@router.get(
    "/{domain_id}",
    response_model=DomainResponse,
)
def get_domain(
    tenant_id: UUID,
    domain_id: UUID,
    service: DomainServiceDependency,
) -> DomainResponse:
    """Return a domain within a tenant."""

    try:
        domain = service.get_by_id(
            tenant_id,
            domain_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return DomainResponse.model_validate(domain)


@router.put(
    "/{domain_id}",
    response_model=DomainResponse,
)
def update_domain(
    tenant_id: UUID,
    domain_id: UUID,
    request: DomainUpdate,
    service: DomainServiceDependency,
) -> DomainResponse:
    """Update a domain within a tenant."""

    try:
        domain = service.update(
            tenant_id,
            domain_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return DomainResponse.model_validate(domain)