"""
Processing Job model.

Represents an individual processing step within an ingestion pipeline.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.entity import Entity
from backend.models.enums import PipelineStage, ProcessingJobStatus

if TYPE_CHECKING:
    from backend.models.ingestion import Ingestion


class ProcessingJob(Entity):
    """
    Individual processing step executed during an ingestion.

    Examples
    --------
    - Validation
    - Extraction
    - Chunking
    - Embedding
    - Vector Indexing
    """

    __tablename__ = "processing_jobs"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    ingestion_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingestions.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Job Information
    # ------------------------------------------------------------------

    stage: Mapped[PipelineStage] = mapped_column(
        Enum(
            PipelineStage,
            name="pipeline_stage",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[ProcessingJobStatus] = mapped_column(
        Enum(
            ProcessingJobStatus,
            name="processing_job_status",
        ),
        nullable=False,
        default=ProcessingJobStatus.PENDING,
        index=True,
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
    )

    records_processed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    ingestion: Mapped["Ingestion"] = relationship(
        "Ingestion",
        back_populates="processing_jobs",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"ProcessingJob("
            f"id={self.id}, "
            f"stage='{self.stage.value}', "
            f"status='{self.status.value}')"
        )
