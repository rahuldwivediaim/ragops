"""
Authorization user model.

Represents the authenticated identity used by the authorization layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class User:
    """
    Represents an authenticated user.

    Parameters
    ----------
    user_id
        Stable identity of the user.

    roles
        Role identifiers assigned to the user.

    tenant_id
        Optional tenant identifier for future multi-tenant
        authorization.

    attributes
        Optional user attributes that can later support
        attribute-based authorization.
    """

    user_id: str
    roles: frozenset[str]
    tenant_id: str | None = None
    attributes: frozenset[tuple[str, str]] = frozenset()

    def __post_init__(self) -> None:
        """Validate the user identity."""

        if not self.user_id.strip():
            raise ValueError("User id cannot be empty.")

        if self.tenant_id is not None and not self.tenant_id.strip():
            raise ValueError("Tenant id cannot be empty.")

    def has_role(self, role_id: str) -> bool:
        """
        Return whether the user has the specified role.
        """

        return role_id in self.roles

    def has_attribute(
        self,
        name: str,
        value: str,
    ) -> bool:
        """
        Return whether the user has the specified attribute.

        This provides an ABAC-ready extension point without
        implementing ABAC yet.
        """

        return (name, value) in self.attributes


__all__ = ["User"]
