"""
Pydantic schemas for domain management.

Domains are tenant-scoped business classifications and may form
a parent/child hierarchy.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import DomainStatus


class DomainCreate(BaseModel):
    """Request schema for creating a domain."""

    tenant_id: UUID = Field(
        ...,
        description="Tenant that owns the domain.",
    )

    code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique domain code within the tenant.",
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Domain name.",
    )

    description: str | None = Field(
        default=None,
        description="Domain description.",
    )

    parent_id: UUID | None = Field(
        default=None,
        description="Optional parent domain.",
    )


class DomainUpdate(BaseModel):
    """Request schema for updating a domain."""

    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Domain code within the tenant.",
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Domain name.",
    )

    description: str | None = Field(
        default=None,
        description="Domain description.",
    )

    parent_id: UUID | None = Field(
        default=None,
        description="Optional parent domain.",
    )

    status: DomainStatus | None = Field(
        default=None,
        description="Domain status.",
    )


class DomainResponse(BaseModel):
    """Response schema for a domain."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    tenant_id: UUID
    parent_id: UUID | None
    code: str
    name: str
    description: str | None
    status: DomainStatus