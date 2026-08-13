"""
Role Registry.

Converts configured authorization roles into runtime Role models
and provides runtime lookup.
"""

from __future__ import annotations

from collections.abc import Mapping

from backend.authorization.models.permission import Permission
from backend.authorization.models.role import Role
from backend.common.config.authorization import (
    PermissionConfig,
    RoleConfig,
)


class RoleRegistry:
    """
    Registry for configured authorization roles.

    The registry translates configuration models into runtime
    authorization models.

    Authorization decisions are intentionally outside the
    responsibility of this class.
    """

    def __init__(
        self,
        roles: Mapping[str, RoleConfig],
        permissions: Mapping[str, PermissionConfig],
    ) -> None:
        self._roles = self._build_roles(
            roles=roles,
            permissions=permissions,
        )

    @classmethod
    def _build_roles(
        cls,
        roles: Mapping[str, RoleConfig],
        permissions: Mapping[str, PermissionConfig],
    ) -> dict[str, Role]:
        """Convert configured roles into runtime Role models."""

        runtime_roles: dict[str, Role] = {}

        for role_id, role_config in roles.items():
            runtime_permissions: set[Permission] = set()

            for permission_id in role_config.permissions:
                permission_config = permissions.get(permission_id)

                if permission_config is None:
                    raise ValueError(
                        f"Role '{role_id}' references unknown "
                        f"permission '{permission_id}'.",
                    )

                runtime_permissions.add(
                    cls._build_permission(
                        permission_id=permission_id,
                        permission_config=permission_config,
                    ),
                )

            runtime_roles[role_id] = Role(
                id=role_id,
                name=role_id,
                permissions=frozenset(runtime_permissions),
                policies=frozenset(role_config.policies),
            )

        return runtime_roles

    @staticmethod
    def _build_permission(
        permission_id: str,
        permission_config: PermissionConfig,
    ) -> Permission:
        """
        Convert configured permission into a runtime Permission.

        The configured action must use the canonical format:

            resource:action

        Examples:

            knowledge:read
            knowledge:write
            document:read
        """

        value = permission_config.action.strip()
        parts = value.split(":")

        if len(parts) != 2:
            raise ValueError(
                f"Permission '{permission_id}' must use the format 'resource:action'.",
            )

        resource, action = (part.strip() for part in parts)

        if not resource or not action:
            raise ValueError(
                f"Permission '{permission_id}' must contain both resource and action.",
            )

        return Permission(
            resource=resource,
            action=action,
        )

    def get(
        self,
        role_id: str,
    ) -> Role:
        """
        Return a runtime role.

        Raises
        ------
        KeyError
            If the role is not configured.
        """

        try:
            return self._roles[role_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown authorization role: {role_id}",
            ) from exc

    def exists(
        self,
        role_id: str,
    ) -> bool:
        """Return whether a role is configured."""

        return role_id in self._roles

    def list_ids(self) -> tuple[str, ...]:
        """Return configured role identifiers."""

        return tuple(self._roles.keys())

    def __len__(self) -> int:
        """Return the number of configured roles."""

        return len(self._roles)


__all__ = ["RoleRegistry"]
