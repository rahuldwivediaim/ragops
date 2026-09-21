"""
Pydantic schemas for tenant management.

A tenant represents an isolated customer or organization
within the RAG Framework.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import TenantStatus


class TenantCreate(BaseModel):
    """Request schema for creating a tenant."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique tenant code.",
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Tenant name.",
    )

    description: str | None = Field(
        default=None,
        description="Tenant description.",
    )


class TenantUpdate(BaseModel):
    """Request schema for updating a tenant."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Tenant name.",
    )

    description: str | None = Field(
        default=None,
        description="Tenant description.",
    )

    status: TenantStatus | None = Field(
        default=None,
        description="Tenant status.",
    )


class TenantResponse(BaseModel):
    """Response schema for a tenant."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    code: str
    name: str
    description: str | None
    status: TenantStatus