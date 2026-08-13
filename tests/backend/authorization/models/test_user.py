"""
Tests for the User model.
"""

import pytest

from backend.authorization.models.user import User


def test_user_creation() -> None:
    user = User(
        user_id="user-001",
        roles=frozenset({"employee"}),
        tenant_id="tenant-001",
    )

    assert user.user_id == "user-001"
    assert user.has_role("employee") is True
    assert user.has_role("admin") is False
    assert user.tenant_id == "tenant-001"


def test_user_supports_attributes() -> None:
    user = User(
        user_id="user-001",
        roles=frozenset({"hr_manager"}),
        attributes=frozenset(
            {
                ("department", "HR"),
                ("country", "IN"),
            }
        ),
    )

    assert user.has_attribute("department", "HR") is True
    assert user.has_attribute("country", "IN") is True
    assert user.has_attribute("department", "Finance") is False


@pytest.mark.parametrize(
    "user_id",
    [
        "",
        "   ",
    ],
)
def test_user_rejects_empty_user_id(
    user_id: str,
) -> None:
    with pytest.raises(ValueError):
        User(
            user_id=user_id,
            roles=frozenset(),
        )


def test_user_rejects_empty_tenant_id() -> None:
    with pytest.raises(ValueError):
        User(
            user_id="user-001",
            roles=frozenset(),
            tenant_id="   ",
        )
