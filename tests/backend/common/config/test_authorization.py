import pytest
from pydantic import ValidationError

from backend.common.config.authorization import (
    AccessPolicyConfig,
    DevelopmentUserConfig,
    PermissionConfig,
    RoleConfig,
)
from backend.common.config.security import AuthorizationConfig


def test_permission_config_creation() -> None:
    permission = PermissionConfig(
        action="knowledge:read",
    )

    assert permission.action == "knowledge:read"


def test_role_config_supports_permissions_and_policies() -> None:
    role = RoleConfig(
        permissions=("knowledge:read",),
        policies=("employee_access",),
    )

    assert role.permissions == ("knowledge:read",)
    assert role.policies == ("employee_access",)


def test_access_policy_config_supports_domains_and_knowledge_bases() -> None:
    policy = AccessPolicyConfig(
        domains=("employee_policies",),
        knowledge_bases=("employee_knowledge_base",),
    )

    assert policy.domains == ("employee_policies",)
    assert policy.knowledge_bases == ("employee_knowledge_base",)


def test_development_user_supports_multiple_roles() -> None:
    user = DevelopmentUserConfig(
        roles=("employee", "finance_manager"),
    )

    assert user.roles == (
        "employee",
        "finance_manager",
    )


def test_authorization_config_supports_atomic_roles() -> None:
    config = AuthorizationConfig(
        default_role="employee",
        permissions={
            "knowledge_read": PermissionConfig(
                action="knowledge:read",
            ),
        },
        roles={
            "employee": RoleConfig(
                permissions=("knowledge_read",),
                policies=("employee_access",),
            ),
        },
        policies={
            "employee_access": AccessPolicyConfig(
                domains=("employee_policies",),
                knowledge_bases=("employee_knowledge_base",),
            ),
        },
    )

    assert config.default_role == "employee"
    assert "employee" in config.roles
    assert "employee_access" in config.policies


def test_authorization_config_supports_multiple_roles_for_user() -> None:
    config = AuthorizationConfig(
        development_users={
            "employee_finance_user": DevelopmentUserConfig(
                roles=(
                    "employee",
                    "finance_manager",
                ),
            ),
        },
    )

    user = config.development_users["employee_finance_user"]

    assert user.roles == (
        "employee",
        "finance_manager",
    )


def test_authorization_config_is_immutable() -> None:
    config = AuthorizationConfig(
        default_role="employee",
    )

    with pytest.raises(ValidationError):
        config.default_role = "admin"  # type: ignore[misc]
