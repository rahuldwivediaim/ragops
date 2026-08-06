"""
Embedding model.

Represents an embedding generated for a chunk during an ingestion run.
Only embedding metadata is stored in PostgreSQL. The actual vector is
stored in the configured vector database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import EXTERNAL_ID_LENGTH
from backend.models.entity import Entity

if TYPE_CHECKING:
    from backend.models.chunk import Chunk
    from backend.models.ingestion import Ingestion
    from backend.models.vector_index import VectorIndex


class Embedding(Entity):
    """
    Embedding metadata.

    One embedding belongs to one chunk and one ingestion.
    """

    __tablename__ = "embeddings"

    __table_args__ = (
        UniqueConstraint(
            "chunk_id",
            "vector_index_id",
            name="uq_chunk_vector_index",
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

    chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=False,
        index=True,
    )

    vector_index_id: Mapped[UUID] = mapped_column(
        ForeignKey("vector_indexes.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Embedding Information
    # ------------------------------------------------------------------

    vector_identifier: Mapped[str] = mapped_column(
        String(EXTERNAL_ID_LENGTH),
        nullable=False,
        unique=True,
        index=True,
    )

    dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    ingestion: Mapped["Ingestion"] = relationship(
        "Ingestion",
        back_populates="embeddings",
        lazy="selectin",
    )

    chunk: Mapped["Chunk"] = relationship(
        "Chunk",
        back_populates="embeddings",
        lazy="selectin",
    )

    vector_index: Mapped["VectorIndex"] = relationship(
        "VectorIndex",
        back_populates="embeddings",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Embedding(id={self.id}, vector_identifier='{self.vector_identifier}')"
