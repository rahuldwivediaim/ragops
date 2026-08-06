"""
Base entity used by all business domain models.
"""

from __future__ import annotations

from backend.models.base import Base
from backend.models.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class Entity(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    """
    Abstract base class for business entities.
    """

    __abstract__ = True
