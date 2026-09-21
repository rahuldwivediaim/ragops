"""
Reusable SQLAlchemy mixins.

Every mixin defined here can be combined to build business entities
without duplicating common columns.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.constants import CODE_LENGTH


class UUIDMixin:
    """
    Adds UUID primary key.
    """

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


class TimestampMixin:
    """
    Adds audit timestamps.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Adds soft delete capability.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class CodeMixin:
    """
    Adds a required human-readable business code.

    Uniqueness is intentionally not defined here because the correct
    uniqueness scope depends on the owning entity.

    Examples:
        Tenant:
            UNIQUE(code)

        Domain:
            UNIQUE(tenant_id, code)

        KnowledgeBase:
            UNIQUE(tenant_id, code)
    """

    code: Mapped[str] = mapped_column(
        String(CODE_LENGTH),
        nullable=False,
        index=True,
    )
