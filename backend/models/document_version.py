"""
Document Version model.

Represents one physical uploaded file for a logical document.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import (
    FILE_EXTENSION_LENGTH,
    FILE_NAME_LENGTH,
    HASH_LENGTH,
    MIME_TYPE_LENGTH,
    PROVIDER_NAME_LENGTH,
    VERSION_LENGTH,
)
from backend.models.entity import Entity

if TYPE_CHECKING:
    from backend.models.document import Document
    from backend.models.ingestion import Ingestion


class DocumentVersion(Entity):
    """
    Physical uploaded version of a document.
    """

    __tablename__ = "document_versions"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "version_number",
            name="uq_document_version_number",
        ),
        Index(
            "ix_document_versions_document_version",
            "document_id",
            "version_number",
        ),
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Version Information
    # ------------------------------------------------------------------

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    version_label: Mapped[str | None] = mapped_column(
        String(VERSION_LENGTH),
    )

    # ------------------------------------------------------------------
    # File Information
    # ------------------------------------------------------------------

    file_name: Mapped[str] = mapped_column(
        String(FILE_NAME_LENGTH),
        nullable=False,
    )

    file_extension: Mapped[str] = mapped_column(
        String(FILE_EXTENSION_LENGTH),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(MIME_TYPE_LENGTH),
        nullable=False,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(HASH_LENGTH),
        nullable=False,
        index=True,
    )

    storage_provider: Mapped[str] = mapped_column(
        String(PROVIDER_NAME_LENGTH),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="versions",
        lazy="selectin",
    )

    ingestions: Mapped[list["Ingestion"]] = relationship(
        "Ingestion",
        back_populates="document_version",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"DocumentVersion("
            f"id={self.id}, "
            f"document_id={self.document_id}, "
            f"version={self.version_number})"
        )
