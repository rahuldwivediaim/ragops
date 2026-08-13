"""
Authorization role model.

Represents a collection of permissions and access-policy references.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.authorization.models.permission import Permission


@dataclass(frozen=True, slots=True)
class Role:
    """
    Represents an RBAC role.

    A role groups permissions together and references the
    access policies that define its resource scope.

    Examples
    --------
    EMPLOYEE
    HR_MANAGER
    FINANCE_MANAGER
    ADMIN
    """

    id: str
    name: str
    permissions: frozenset[Permission]
    policies: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        """Validate the role definition."""

        if not self.id.strip():
            raise ValueError("Role id cannot be empty.")

        if not self.name.strip():
            raise ValueError("Role name cannot be empty.")

        for policy_id in self.policies:
            if not policy_id.strip():
                raise ValueError(
                    "Role policy id cannot be empty.",
                )

    def has_permission(
        self,
        permission: Permission,
    ) -> bool:
        """
        Return whether this role contains the given permission.
        """

        return permission in self.permissions

    def has_policy(
        self,
        policy_id: str,
    ) -> bool:
        """
        Return whether this role references the specified policy.
        """

        return policy_id in self.policies


__all__ = ["Role"]
