"""
Tests for the Role Registry.
"""

import pytest
from pydantic import ValidationError

from backend.authorization.models.permission import Permission
from backend.authorization.models.role import Role
from backend.authorization.registry import RoleRegistry
from backend.common.config.authorization import (
    PermissionConfig,
    RoleConfig,
)


def test_role_registry_converts_configuration_to_runtime_role() -> None:
    registry = RoleRegistry(
        roles={
            "employee": RoleConfig(
                permissions=("knowledge_read",),
                policies=("employee_access",),
            ),
        },
        permissions={
            "knowledge_read": PermissionConfig(
                action="knowledge:read",
            ),
        },
    )

    role = registry.get("employee")

    assert isinstance(role, Role)
    assert role.id == "employee"
    assert role.name == "employee"

    assert role.policies == frozenset(
        {"employee_access"},
    )

    assert role.permissions == frozenset(
        {
            Permission(
                resource="knowledge",
                action="read",
            ),
        },
    )


def test_role_registry_converts_multiple_permissions() -> None:
    registry = RoleRegistry(
        roles={
            "finance_manager": RoleConfig(
                permissions=(
                    "knowledge_read",
                    "knowledge_write",
                ),
            ),
        },
        permissions={
            "knowledge_read": PermissionConfig(
                action="knowledge:read",
            ),
            "knowledge_write": PermissionConfig(
                action="knowledge:write",
            ),
        },
    )

    role = registry.get("finance_manager")

    assert role.has_permission(
        Permission(
            resource="knowledge",
            action="read",
        ),
    )

    assert role.has_permission(
        Permission(
            resource="knowledge",
            action="write",
        ),
    )


def test_role_registry_reports_existing_role() -> None:
    registry = RoleRegistry(
        roles={
            "employee": RoleConfig(),
        },
        permissions={},
    )

    assert registry.exists("employee") is True
    assert registry.exists("finance_manager") is False


def test_role_registry_lists_role_ids() -> None:
    registry = RoleRegistry(
        roles={
            "employee": RoleConfig(),
            "finance_manager": RoleConfig(),
        },
        permissions={},
    )

    assert registry.list_ids() == (
        "employee",
        "finance_manager",
    )


def test_role_registry_unknown_role_raises_key_error() -> None:
    registry = RoleRegistry(
        roles={
            "employee": RoleConfig(),
        },
        permissions={},
    )

    with pytest.raises(
        KeyError,
        match="Unknown authorization role: finance_manager",
    ):
        registry.get("finance_manager")


def test_role_registry_rejects_unknown_permission() -> None:
    with pytest.raises(
        ValueError,
        match=("Role 'employee' references unknown permission 'knowledge_read'"),
    ):
        RoleRegistry(
            roles={
                "employee": RoleConfig(
                    permissions=("knowledge_read",),
                ),
            },
            permissions={},
        )


def test_permission_config_rejects_empty_action() -> None:
    with pytest.raises(ValidationError):
        PermissionConfig(action="")


@pytest.mark.parametrize(
    "permission_action",
    [
        ":read",
        "knowledge:",
        "knowledge:read:extra",
    ],
)
def test_role_registry_rejects_invalid_permission_format(
    permission_action: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "must use the format 'resource:action'"
            if permission_action == "knowledge:read:extra"
            else "must contain both resource and action"
        ),
    ):
        RoleRegistry(
            roles={
                "employee": RoleConfig(
                    permissions=("knowledge_read",),
                ),
            },
            permissions={
                "knowledge_read": PermissionConfig(
                    action=permission_action,
                ),
            },
        )


def test_role_registry_length() -> None:
    registry = RoleRegistry(
        roles={
            "employee": RoleConfig(),
            "finance_manager": RoleConfig(),
        },
        permissions={},
    )

    assert len(registry) == 2
