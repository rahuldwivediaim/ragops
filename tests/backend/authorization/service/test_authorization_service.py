"""
Tests for AuthorizationService.
"""

import pytest

from backend.authorization.models.permission import Permission
from backend.authorization.models.user import User
from backend.authorization.registry import (
    AccessPolicyRegistry,
    RoleRegistry,
)
from backend.authorization.service import AuthorizationService
from backend.common.config.authorization import (
    AccessPolicyConfig,
    PermissionConfig,
    RoleConfig,
)


def create_service() -> AuthorizationService:
    """Create a representative authorization service."""

    role_registry = RoleRegistry(
        roles={
            "employee": RoleConfig(
                permissions=("knowledge_read",),
                policies=("employee_access",),
            ),
            "finance_manager": RoleConfig(
                permissions=(
                    "knowledge_read",
                    "knowledge_write",
                ),
                policies=("finance_access",),
            ),
            "hr_manager": RoleConfig(
                permissions=("knowledge_read",),
                policies=("hr_access",),
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

    access_policy_registry = AccessPolicyRegistry(
        policies={
            "employee_access": AccessPolicyConfig(
                domains=("employee_policies",),
                knowledge_bases=("employee_kb",),
            ),
            "finance_access": AccessPolicyConfig(
                domains=("finance_policies",),
                knowledge_bases=("finance_kb",),
            ),
            "hr_access": AccessPolicyConfig(
                domains=("employee_policies",),
                knowledge_bases=("hr_kb",),
            ),
        },
    )

    return AuthorizationService(
        role_registry=role_registry,
        access_policy_registry=access_policy_registry,
    )


def test_employee_can_read_knowledge() -> None:
    service = create_service()

    user = User(
        user_id="employee_user",
        roles=frozenset({"employee"}),
    )

    permission = Permission(
        resource="knowledge",
        action="read",
    )

    assert (
        service.has_permission(
            user,
            permission,
        )
        is True
    )


def test_employee_cannot_write_knowledge() -> None:
    service = create_service()

    user = User(
        user_id="employee_user",
        roles=frozenset({"employee"}),
    )

    permission = Permission(
        resource="knowledge",
        action="write",
    )

    assert (
        service.has_permission(
            user,
            permission,
        )
        is False
    )


def test_permission_authorization_returns_allow_decision() -> None:
    service = create_service()

    user = User(
        user_id="employee_user",
        roles=frozenset({"employee"}),
    )

    permission = Permission(
        resource="knowledge",
        action="read",
    )

    decision = service.authorize_permission(
        user,
        permission,
    )

    assert decision.allowed is True
    assert "employee" in decision.reason


def test_permission_authorization_returns_deny_decision() -> None:
    service = create_service()

    user = User(
        user_id="employee_user",
        roles=frozenset({"employee"}),
    )

    permission = Permission(
        resource="knowledge",
        action="write",
    )

    decision = service.authorize_permission(
        user,
        permission,
    )

    assert decision.allowed is False
    assert "does not have permission" in decision.reason


def test_employee_gets_employee_access_scope() -> None:
    service = create_service()

    user = User(
        user_id="employee_user",
        roles=frozenset({"employee"}),
    )

    scope = service.get_access_scope(user)

    assert scope.domains == frozenset(
        {"employee_policies"},
    )

    assert scope.knowledge_bases == frozenset(
        {"employee_kb"},
    )


def test_finance_manager_gets_finance_access_scope() -> None:
    service = create_service()

    user = User(
        user_id="finance_user",
        roles=frozenset({"finance_manager"}),
    )

    scope = service.get_access_scope(user)

    assert scope.domains == frozenset(
        {"finance_policies"},
    )

    assert scope.knowledge_bases == frozenset(
        {"finance_kb"},
    )


def test_multiple_roles_produce_union_of_access_scope() -> None:
    """
    Core architectural requirement:

    employee + finance_manager
        ->
    employee access + finance access
    """

    service = create_service()

    user = User(
        user_id="employee_finance_user",
        roles=frozenset(
            {
                "employee",
                "finance_manager",
            },
        ),
    )

    scope = service.get_access_scope(user)

    assert scope.domains == frozenset(
        {
            "employee_policies",
            "finance_policies",
        },
    )

    assert scope.knowledge_bases == frozenset(
        {
            "employee_kb",
            "finance_kb",
        },
    )


def test_multiple_roles_union_permissions() -> None:
    service = create_service()

    user = User(
        user_id="employee_finance_user",
        roles=frozenset(
            {
                "employee",
                "finance_manager",
            },
        ),
    )

    assert (
        service.has_permission(
            user,
            Permission(
                resource="knowledge",
                action="read",
            ),
        )
        is True
    )

    assert (
        service.has_permission(
            user,
            Permission(
                resource="knowledge",
                action="write",
            ),
        )
        is True
    )


def test_domain_authorization() -> None:
    service = create_service()

    user = User(
        user_id="employee_finance_user",
        roles=frozenset(
            {
                "employee",
                "finance_manager",
            },
        ),
    )

    assert (
        service.is_domain_authorized(
            user,
            "employee_policies",
        )
        is True
    )

    assert (
        service.is_domain_authorized(
            user,
            "finance_policies",
        )
        is True
    )

    assert (
        service.is_domain_authorized(
            user,
            "technical_documentation",
        )
        is False
    )


def test_knowledge_base_authorization() -> None:
    service = create_service()

    user = User(
        user_id="employee_finance_user",
        roles=frozenset(
            {
                "employee",
                "finance_manager",
            },
        ),
    )

    assert (
        service.is_knowledge_base_authorized(
            user,
            "employee_kb",
        )
        is True
    )

    assert (
        service.is_knowledge_base_authorized(
            user,
            "finance_kb",
        )
        is True
    )

    assert (
        service.is_knowledge_base_authorized(
            user,
            "technical_kb",
        )
        is False
    )


def test_user_without_roles_has_no_access() -> None:
    service = create_service()

    user = User(
        user_id="unassigned_user",
        roles=frozenset(),
    )

    assert service.get_access_scope(user).domains == frozenset()

    assert (
        service.has_permission(
            user,
            Permission(
                resource="knowledge",
                action="read",
            ),
        )
        is False
    )


def test_unknown_role_fails_closed() -> None:
    service = create_service()

    user = User(
        user_id="unknown_role_user",
        roles=frozenset({"does_not_exist"}),
    )

    with pytest.raises(
        KeyError,
        match="Unknown authorization role: does_not_exist",
    ):
        service.get_access_scope(user)


def test_service_rejects_role_with_unknown_policy() -> None:
    role_registry = RoleRegistry(
        roles={
            "employee": RoleConfig(
                policies=("missing_policy",),
            ),
        },
        permissions={},
    )

    access_policy_registry = AccessPolicyRegistry(
        policies={},
    )

    with pytest.raises(
        ValueError,
        match=(
            "Role 'employee' references unknown authorization policy 'missing_policy'"
        ),
    ):
        AuthorizationService(
            role_registry=role_registry,
            access_policy_registry=access_policy_registry,
        )
