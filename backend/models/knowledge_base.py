"""
Knowledge Base model.

A Knowledge Base represents a logical collection of related documents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import (
    LANGUAGE_LENGTH,
    NAME_LENGTH,
)
from backend.models.entity import Entity
from backend.models.enums import KnowledgeBaseStatus
from backend.models.mixins import CodeMixin

if TYPE_CHECKING:
    from backend.models.document import Document


class KnowledgeBase(CodeMixin, Entity):
    """
    Logical collection of business documents.

    Example:
        - HR Policies
        - Finance SOP
        - IT Knowledge Base
        - Product Documentation
    """

    __tablename__ = "knowledge_bases"

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

    status: Mapped[KnowledgeBaseStatus] = mapped_column(
        Enum(
            KnowledgeBaseStatus,
            name="knowledge_base_status",
        ),
        default=KnowledgeBaseStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    owner: Mapped[str | None] = mapped_column(
        String(NAME_LENGTH),
        nullable=True,
    )

    default_language: Mapped[str] = mapped_column(
        String(LANGUAGE_LENGTH),
        default="en",
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Object Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"KnowledgeBase(id={self.id}, code='{self.code}', name='{self.name}')"
