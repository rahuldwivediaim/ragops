"""
Ingestion model.

Represents a single end-to-end RAG ingestion run for one document version.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.entity import Entity
from backend.models.enums import IngestionStatus

if TYPE_CHECKING:
    from backend.models.chunk import Chunk
    from backend.models.document_version import DocumentVersion
    from backend.models.embedding import Embedding
    from backend.models.embedding_profile import EmbeddingProfile
    from backend.models.pipeline_event import PipelineEvent
    from backend.models.processing_job import ProcessingJob
    from backend.models.vector_index import VectorIndex


class Ingestion(Entity):
    """
    Root entity for one complete ingestion execution.

    Every upload/reprocessing operation creates one Ingestion record.
    All downstream pipeline entities reference this record.
    """

    __tablename__ = "ingestions"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id"),
        nullable=False,
        index=True,
    )

    embedding_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("embedding_profiles.id"),
        nullable=False,
        index=True,
    )

    vector_index_id: Mapped[UUID] = mapped_column(
        ForeignKey("vector_indexes.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Execution Information
    # ------------------------------------------------------------------

    status: Mapped[IngestionStatus] = mapped_column(
        Enum(
            IngestionStatus,
            name="ingestion_status",
        ),
        nullable=False,
        default=IngestionStatus.PENDING,
        index=True,
    )

    trigger_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="MANUAL",
    )

    initiated_by: Mapped[str | None] = mapped_column(
        String(100),
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
    )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    total_chunks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    successful_chunks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    failed_chunks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_embeddings: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_vectors_written: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    document_version: Mapped["DocumentVersion"] = relationship(
        "DocumentVersion",
        back_populates="ingestions",
        lazy="selectin",
    )

    embedding_profile: Mapped["EmbeddingProfile"] = relationship(
        "EmbeddingProfile",
        back_populates="ingestions",
        lazy="selectin",
    )

    vector_index: Mapped["VectorIndex"] = relationship(
        "VectorIndex",
        back_populates="ingestions",
        lazy="selectin",
    )

    processing_jobs: Mapped[list["ProcessingJob"]] = relationship(
        "ProcessingJob",
        back_populates="ingestion",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    pipeline_events: Mapped[list["PipelineEvent"]] = relationship(
        "PipelineEvent",
        back_populates="ingestion",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk",
        back_populates="ingestion",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding",
        back_populates="ingestion",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Ingestion(id={self.id}, status='{self.status.value}')"
