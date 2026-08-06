"""
Embedding Profile model.

Defines the configuration of an embedding model used to generate vectors.
Multiple VectorIndex records can reference the same EmbeddingProfile.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Integer, String, Text

from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import (
    MODEL_NAME_LENGTH,
    NAME_LENGTH,
)
from backend.models.entity import Entity
from backend.models.enums import EmbeddingProvider

if TYPE_CHECKING:
    from backend.models.vector_index import VectorIndex
    from backend.models.ingestion import Ingestion


class EmbeddingProfile(Entity):
    """
    Embedding model configuration.

    Examples
    --------
    - OpenAI text-embedding-3-small
    - OpenAI text-embedding-3-large
    - Nomic Embed Text
    - BAAI BGE Large
    """

    __tablename__ = "embedding_profiles"

    # ------------------------------------------------------------------
    # Business Information
    # ------------------------------------------------------------------

    name: Mapped[str] = mapped_column(
        String(NAME_LENGTH),
        nullable=False,
        unique=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    provider: Mapped[EmbeddingProvider] = mapped_column(
        Enum(
            EmbeddingProvider,
            name="embedding_provider",
        ),
        nullable=False,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(MODEL_NAME_LENGTH),
        nullable=False,
    )

    dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    max_tokens: Mapped[int | None] = mapped_column(
        Integer,
    )

    default_chunk_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1000,
    )

    default_chunk_overlap: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=200,
    )

    normalize_embeddings: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    vector_indexes: Mapped[list["VectorIndex"]] = relationship(
        "VectorIndex",
        back_populates="embedding_profile",
        lazy="selectin",
    )

    ingestions: Mapped[list["Ingestion"]] = relationship(
        "Ingestion",
        back_populates="embedding_profile",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"EmbeddingProfile("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"provider='{self.provider.value}', "
            f"model='{self.model_name}')"
        )
