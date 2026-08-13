"""
Tests for the Permission model.
"""

import pytest

from backend.authorization.models.permission import Permission


def test_permission_creation() -> None:
    permission = Permission(
        resource="knowledge",
        action="read",
    )

    assert permission.resource == "knowledge"
    assert permission.action == "read"
    assert permission.key == "knowledge:read"


@pytest.mark.parametrize(
    ("resource", "action"),
    [
        ("", "read"),
        ("   ", "read"),
        ("knowledge", ""),
        ("knowledge", "   "),
    ],
)
def test_permission_rejects_empty_values(
    resource: str,
    action: str,
) -> None:
    with pytest.raises(ValueError):
        Permission(
            resource=resource,
            action=action,
        )


def test_permissions_with_same_values_are_equal() -> None:
    first = Permission("knowledge", "read")
    second = Permission("knowledge", "read")

    assert first == second
