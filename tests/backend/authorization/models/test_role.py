"""
Tests for the Role model.
"""

import pytest

from backend.authorization.models.permission import Permission
from backend.authorization.models.role import Role


def test_role_creation() -> None:
    permission = Permission(
        resource="knowledge",
        action="read",
    )

    role = Role(
        id="employee",
        name="Employee",
        permissions=frozenset({permission}),
    )

    assert role.id == "employee"
    assert role.name == "Employee"
    assert role.has_permission(permission) is True
    assert role.policies == frozenset()


def test_role_creation_with_policies() -> None:
    permission = Permission(
        resource="knowledge",
        action="read",
    )

    role = Role(
        id="employee",
        name="Employee",
        permissions=frozenset({permission}),
        policies=frozenset({"employee_access"}),
    )

    assert role.has_policy("employee_access") is True
    assert role.has_policy("finance_access") is False


def test_role_rejects_missing_permission() -> None:
    read_permission = Permission("knowledge", "read")
    write_permission = Permission("knowledge", "write")

    role = Role(
        id="employee",
        name="Employee",
        permissions=frozenset({read_permission}),
    )

    assert role.has_permission(write_permission) is False


@pytest.mark.parametrize(
    ("role_id", "name"),
    [
        ("", "Employee"),
        ("   ", "Employee"),
        ("employee", ""),
        ("employee", "   "),
    ],
)
def test_role_rejects_empty_values(
    role_id: str,
    name: str,
) -> None:
    with pytest.raises(ValueError):
        Role(
            id=role_id,
            name=name,
            permissions=frozenset(),
        )


def test_role_rejects_empty_policy_id() -> None:
    with pytest.raises(ValueError):
        Role(
            id="employee",
            name="Employee",
            permissions=frozenset(),
            policies=frozenset({"   "}),
        )
