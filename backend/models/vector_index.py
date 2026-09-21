"""
Vector Index model.

Represents a physical vector database index or collection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import NAME_LENGTH
from backend.models.entity import Entity
from backend.models.enums import (
    StorageProvider,
    VectorInfrastructureMode,
    VectorProvider,
)

if TYPE_CHECKING:
    from backend.models.embedding import Embedding
    from backend.models.embedding_profile import EmbeddingProfile
    from backend.models.ingestion import Ingestion


class VectorIndex(Entity):
    """
    Physical vector database index.

    Examples
    --------
    - HR Pinecone Index
    - Finance Pinecone Index
    - Legal pgvector Collection
    """

    __tablename__ = "vector_indexes"

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "index_name",
            name="uq_vector_provider_index",
        ),
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    embedding_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("embedding_profiles.id"),
        nullable=False,
        index=True,
    )

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

    provider: Mapped[VectorProvider] = mapped_column(
        Enum(
            VectorProvider,
            name="vector_provider",
        ),
        nullable=False,
        index=True,
    )

    index_name: Mapped[str] = mapped_column(
        String(NAME_LENGTH),
        nullable=False,
    )

    namespace: Mapped[str | None] = mapped_column(
        String(NAME_LENGTH),
    )

    dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    management_mode: Mapped[VectorInfrastructureMode] = mapped_column(
        Enum(
            VectorInfrastructureMode,
            name="vector_infrastructure_mode",
        ),
        nullable=False,
        default=VectorInfrastructureMode.RAGOPS_MANAGED,
    )

    storage_provider: Mapped[StorageProvider] = mapped_column(
        Enum(
            StorageProvider,
            name="storage_provider",
        ),
        nullable=False,
        default=StorageProvider.LOCAL,
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

    embedding_profile: Mapped["EmbeddingProfile"] = relationship(
        "EmbeddingProfile",
        back_populates="vector_indexes",
        lazy="selectin",
    )

    ingestions: Mapped[list["Ingestion"]] = relationship(
        "Ingestion",
        back_populates="vector_index",
        lazy="selectin",
    )

    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding",
        back_populates="vector_index",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"VectorIndex("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"provider='{self.provider.value}', "
            f"index='{self.index_name}', "
            f"management_mode='{self.management_mode.value}')"
        )