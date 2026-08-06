"""
backend/common/metadata.py

Common metadata models for the RAGOps platform.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .types import CorrelationId, RequestId


class PageMetadata(BaseModel):
    """Pagination metadata."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_records: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool = False
    has_previous: bool = False


class ResponseMetadata(BaseModel):
    """Standard response metadata."""

    model_config = ConfigDict(extra="forbid")

    request_id: RequestId | None = None
    correlation_id: CorrelationId | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    api_version: str = "v1"
    service_version: str = "1.0.0"
    processing_time_ms: float | None = Field(default=None, ge=0)
    page: PageMetadata | None = None
    additional: dict[str, Any] = Field(default_factory=dict)


class AuditMetadata(BaseModel):
    """Audit information."""

    model_config = ConfigDict(extra="forbid")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    updated_by: str | None = None


class DocumentMetadata(BaseModel):
    """Document metadata."""

    model_config = ConfigDict(extra="allow")

    document_id: str
    title: str | None = None
    owner: str | None = None
    department: str | None = None
    classification: str | None = None
    tags: list[str] = Field(default_factory=list)
    language: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class ChunkMetadata(BaseModel):
    """Chunk metadata."""

    model_config = ConfigDict(extra="allow")

    chunk_id: str
    document_id: str
    sequence: int
    token_count: int | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "PageMetadata",
    "ResponseMetadata",
    "AuditMetadata",
    "DocumentMetadata",
    "ChunkMetadata",
]
