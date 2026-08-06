"""
Document Upload Schemas

Request/Response models for document upload operations.

Author: RAGOps
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentUploadResponse(BaseModel):
    """
    Response returned after a successful document upload.
    """

    model_config = ConfigDict(from_attributes=True)

    document_id: UUID

    version_id: UUID

    knowledge_base_id: UUID

    filename: str

    original_filename: str

    content_type: str

    size_bytes: int

    storage_path: str

    status: str

    uploaded_at: datetime


class DocumentMetadata(BaseModel):
    """
    Optional metadata supplied with an uploaded document.
    """

    title: str | None = Field(
        default=None,
        max_length=255,
        description="Document title",
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Document description",
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Optional document tags",
    )
