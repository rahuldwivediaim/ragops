"""
Tenant model.

A tenant represents an isolated customer or organization within
the RAG Framework.

Tenant is the root of the application data hierarchy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import NAME_LENGTH
from backend.models.entity import Entity
from backend.models.enums import TenantStatus
from backend.models.mixins import CodeMixin

if TYPE_CHECKING:
    from backend.models.domain import Domain
    from backend.models.knowledge_base import KnowledgeBase


class Tenant(CodeMixin, Entity):
    """
    Represents an isolated customer organization.

    Tenant is the root ownership boundary for business data.

    Examples
    --------
    ACME
    CONTOSO
    ORACLE_INTERNAL
    """

    __tablename__ = "tenants"

    __table_args__ = (
        UniqueConstraint(
            "code",
            name="uq_tenants_code",
        ),
    )

    name: Mapped[str] = mapped_column(
        String(NAME_LENGTH),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[TenantStatus] = mapped_column(
        Enum(
            TenantStatus,
            name="tenant_status",
        ),
        default=TenantStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    domains: Mapped[list["Domain"]] = relationship(
        "Domain",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    knowledge_bases: Mapped[list["KnowledgeBase"]] = relationship(
        "KnowledgeBase",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"Tenant(id={self.id}, code='{self.code}', "
            f"name='{self.name}', status='{self.status.value}')"
        )
