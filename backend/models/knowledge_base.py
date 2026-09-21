"""
Knowledge Base model.

A Knowledge Base is a logical collection of knowledge belonging
to exactly one domain within exactly one tenant.

Relationship:

    Tenant
        └── Domain
              └── Knowledge Base
                    └── Documents
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import (
    CODE_LENGTH,
    LANGUAGE_LENGTH,
    NAME_LENGTH,
)
from backend.models.entity import Entity
from backend.models.enums import KnowledgeBaseStatus

if TYPE_CHECKING:
    from backend.models.document import Document
    from backend.models.domain import Domain
    from backend.models.tenant import Tenant


class KnowledgeBase(Entity):
    """
    Logical collection of business documents.

    A Knowledge Base belongs to exactly one Domain.

    Example
    -------
    Tenant:
        ACME

    Domain:
        HR -> Payroll -> Payroll Tax

    Knowledge Base:
        Payroll Tax Policies
    """

    __tablename__ = "knowledge_bases"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "code",
            name="uq_knowledge_bases_tenant_code",
        ),
        UniqueConstraint(
            "tenant_id",
            "name",
            name="uq_knowledge_bases_tenant_name",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "tenants.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    domain_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "domains.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(CODE_LENGTH),
        nullable=False,
        index=True,
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

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="knowledge_bases",
        lazy="selectin",
    )

    domain: Mapped["Domain"] = relationship(
        "Domain",
        back_populates="knowledge_bases",
        lazy="selectin",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"KnowledgeBase(id={self.id}, code='{self.code}', "
            f"name='{self.name}', domain_id={self.domain_id})"
        )
