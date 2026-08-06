"""
Document model.

A Document represents a logical business document within a Knowledge Base.
Each document can have multiple physical versions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import (
    EXTERNAL_ID_LENGTH,
    NAME_LENGTH,
    TITLE_LENGTH,
)
from backend.models.entity import Entity
from backend.models.enums import (
    DocumentSource,
    DocumentStatus,
    DocumentType,
)

if TYPE_CHECKING:
    from backend.models.document_version import DocumentVersion
    from backend.models.knowledge_base import KnowledgeBase


class Document(Entity):
    """
    Logical business document.

    A document is versioned through the DocumentVersion table.
    """

    __tablename__ = "documents"

    __table_args__ = (
        Index(
            "ix_documents_kb_status",
            "knowledge_base_id",
            "status",
        ),
        UniqueConstraint(
            "knowledge_base_id",
            "title",
            name="uq_document_title_per_kb",
        ),
    )

    # ------------------------------------------------------------------
    # Relationships (Foreign Keys)
    # ------------------------------------------------------------------

    knowledge_base_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_bases.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Business Information
    # ------------------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(TITLE_LENGTH),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(
            DocumentType,
            name="document_type",
        ),
        nullable=False,
    )

    source: Mapped[DocumentSource] = mapped_column(
        Enum(
            DocumentSource,
            name="document_source",
        ),
        nullable=False,
    )

    source_reference: Mapped[str | None] = mapped_column(
        String(EXTERNAL_ID_LENGTH),
    )

    owner: Mapped[str | None] = mapped_column(
        String(NAME_LENGTH),
    )

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            name="document_status",
        ),
        default=DocumentStatus.PENDING,
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase",
        back_populates="documents",
        lazy="selectin",
    )

    versions: Mapped[list["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Document("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status='{self.status.value}')"
        )
