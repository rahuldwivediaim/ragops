"""
File:
    backend/schemas/knowledge_base.py

Purpose:
    Pydantic schemas for Knowledge Base API.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import KnowledgeBaseStatus


class KnowledgeBaseCreate(BaseModel):
    """Request schema for creating a knowledge base."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique knowledge base code.",
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
    """Request schema for updating a knowledge base."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    owner: str | None = Field(
        default=None,
        max_length=200,
    )

    default_language: str | None = Field(
        default=None,
        max_length=10,
    )

    status: KnowledgeBaseStatus | None = None


class KnowledgeBaseResponse(BaseModel):
    """Knowledge Base response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    code: str

    name: str

    description: str | None

    owner: str | None

    default_language: str

    status: KnowledgeBaseStatus

    created_at: datetime

    updated_at: datetime


class KnowledgeBaseListResponse(BaseModel):
    """Knowledge Base list response."""

    items: list[KnowledgeBaseResponse]

    total: int
