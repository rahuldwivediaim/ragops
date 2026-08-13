"""
Authorization permission model.

Represents an action that a principal is allowed to perform
against a logical resource.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Permission:
    """
    Represents an authorization permission.

    Examples
    --------
    knowledge:read
    knowledge:write
    document:read
    """

    resource: str
    action: str

    def __post_init__(self) -> None:
        """Validate the permission definition."""

        if not self.resource.strip():
            raise ValueError("Permission resource cannot be empty.")

        if not self.action.strip():
            raise ValueError("Permission action cannot be empty.")

    @property
    def key(self) -> str:
        """Return the canonical permission key."""

        return f"{self.resource}:{self.action}"


__all__ = ["Permission"]
