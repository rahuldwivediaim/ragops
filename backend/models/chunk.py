"""
Chunk model.

Represents a single text chunk generated from a document version during
an ingestion run.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.entity import Entity

if TYPE_CHECKING:
    from backend.models.embedding import Embedding
    from backend.models.ingestion import Ingestion


class Chunk(Entity):
    """
    Text chunk generated from a document.

    Every chunk belongs to exactly one ingestion.
    """

    __tablename__ = "chunks"

    __table_args__ = (
        UniqueConstraint(
            "ingestion_id",
            "chunk_number",
            name="uq_chunk_number_per_ingestion",
        ),
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    ingestion_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingestions.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Chunk Information
    # ------------------------------------------------------------------

    chunk_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    character_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    character_end: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    token_count: Mapped[int | None] = mapped_column(
        Integer,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    ingestion: Mapped["Ingestion"] = relationship(
        "Ingestion",
        back_populates="chunks",
        lazy="selectin",
    )

    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding",
        back_populates="chunk",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Chunk("
            f"id={self.id}, "
            f"chunk_number={self.chunk_number}, "
            f"tokens={self.token_count})"
        )
