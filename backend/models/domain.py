"""
Persistent Domain model.

A Domain represents a logical business classification within a tenant.

Domains may form a hierarchy:

    HR
      └── Payroll
            └── Payroll Tax

A Domain is independent of vector stores, embedding providers,
rerankers, AI agents and authorization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.constants import CODE_LENGTH, NAME_LENGTH
from backend.models.entity import Entity
from backend.models.enums import DomainStatus

if TYPE_CHECKING:
    from backend.models.knowledge_base import KnowledgeBase
    from backend.models.tenant import Tenant


class Domain(Entity):
    """
    Persistent business domain.

    Domains are tenant-scoped and may form a parent/child hierarchy.

    Examples
    --------
    HR
    HR -> Payroll
    HR -> Payroll -> Payroll Tax
    Finance
    Finance -> Accounts Payable
    """

    __tablename__ = "domains"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "code",
            name="uq_domains_tenant_code",
        ),
        UniqueConstraint(
            "tenant_id",
            "name",
            name="uq_domains_tenant_name",
        ),
        CheckConstraint(
            "parent_id IS NULL OR parent_id <> id",
            name="not_self_parent",
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

    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "domains.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
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

    status: Mapped[DomainStatus] = mapped_column(
        Enum(
            DomainStatus,
            name="domain_status",
        ),
        default=DomainStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="domains",
        lazy="selectin",
    )

    parent: Mapped["Domain | None"] = relationship(
        "Domain",
        remote_side="Domain.id",
        back_populates="children",
        lazy="selectin",
    )

    children: Mapped[list["Domain"]] = relationship(
        "Domain",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    knowledge_bases: Mapped[list["KnowledgeBase"]] = relationship(
        "KnowledgeBase",
        back_populates="domain",
        lazy="selectin",
    )

    @property
    def is_root(self) -> bool:
        """Return whether this domain has no parent domain."""

        return self.parent is None

    def __repr__(self) -> str:
        return (
            f"Domain(id={self.id}, code='{self.code}', "
            f"name='{self.name}', parent_id={self.parent_id})"
        )
