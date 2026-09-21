"""
Pydantic schemas for Knowledge Base API.

A Knowledge Base belongs to exactly one tenant and one domain.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import KnowledgeBaseStatus


class KnowledgeBaseCreate(BaseModel):
    """Request schema for creating a Knowledge Base."""

    tenant_id: UUID = Field(
        ...,
        description="Tenant that owns the knowledge base.",
    )

    domain_id: UUID = Field(
        ...,
        description="Domain that owns the knowledge base.",
    )

    code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique knowledge base code within the tenant.",
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Knowledge base name.",
    )

    description: str | None = Field(
        default=None,
        description="Knowledge base description.",
    )

    owner: str | None = Field(
        default=None,
        max_length=200,
        description="Knowledge base owner.",
    )

    default_language: str = Field(
        default="en",
        max_length=10,
        description="Default language.",
    )


class KnowledgeBaseUpdate(BaseModel):
    """Request schema for updating a Knowledge Base."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Knowledge base name.",
    )

    description: str | None = Field(
        default=None,
        description="Knowledge base description.",
    )

    owner: str | None = Field(
        default=None,
        max_length=200,
        description="Knowledge base owner.",
    )

    default_language: str | None = Field(
        default=None,
        max_length=10,
        description="Default language.",
    )

    status: KnowledgeBaseStatus | None = Field(
        default=None,
        description="Knowledge base status.",
    )


class KnowledgeBaseResponse(BaseModel):
    """Response schema for a Knowledge Base."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    tenant_id: UUID
    domain_id: UUID
    code: str
    name: str
    description: str | None
    owner: str | None
    default_language: str
    status: KnowledgeBaseStatus
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseListResponse(BaseModel):
    """Response schema for a Knowledge Base list."""

    items: list[KnowledgeBaseResponse]
    total: int