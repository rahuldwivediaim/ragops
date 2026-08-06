"""
Pipeline Event model.

Represents an event generated during an ingestion pipeline execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.entity import Entity
from backend.models.enums import PipelineStage

if TYPE_CHECKING:
    from backend.models.ingestion import Ingestion


class PipelineEvent(Entity):
    """
    Audit event generated during pipeline execution.
    """

    __tablename__ = "pipeline_events"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    ingestion_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingestions.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Event Information
    # ------------------------------------------------------------------

    stage: Mapped[PipelineStage] = mapped_column(
        Enum(
            PipelineStage,
            name="pipeline_stage",
        ),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    details: Mapped[str | None] = mapped_column(
        Text,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    ingestion: Mapped["Ingestion"] = relationship(
        "Ingestion",
        back_populates="pipeline_events",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"PipelineEvent("
            f"id={self.id}, "
            f"stage='{self.stage.value}', "
            f"event_type='{self.event_type}')"
        )
