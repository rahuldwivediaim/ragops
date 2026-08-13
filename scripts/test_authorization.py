"""
Authorization framework smoke test.

Demonstrates:
- Atomic roles.
- Permission evaluation.
- Domain authorization.
- Knowledge-base authorization.
- Union of access across multiple roles.
"""

from __future__ import annotations

from backend.authorization.models import Permission, User
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


def create_authorization_service() -> AuthorizationService:
    """Create the authorization service used by the smoke test."""

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
        },
    )

    return AuthorizationService(
        role_registry=role_registry,
        access_policy_registry=access_policy_registry,
    )


def print_permission_result(
    service: AuthorizationService,
    user: User,
    permission: Permission,
) -> None:
    """Print the authorization result for a permission."""

    status = "ALLOWED" if service.has_permission(user, permission) else "DENIED"

    print(
        f"  {permission.key:<20} {status}",
    )


def print_scope_result(
    service: AuthorizationService,
    user: User,
    values: tuple[str, ...],
    *,
    resource_type: str,
) -> None:
    """Print authorization results for domains or knowledge bases."""

    scope = service.get_access_scope(user)

    if resource_type == "domain":
        authorized = scope.domains
    else:
        authorized = scope.knowledge_bases

    for value in values:
        marker = "✓" if value in authorized else "✗"
        print(f"  {marker} {value}")


def print_user_test(
    service: AuthorizationService,
    user: User,
) -> None:
    """Print authorization results for one user."""

    print("------------------------------------------------------------")
    print()
    print(f"User: {user.user_id}")

    roles = ", ".join(sorted(user.roles))
    print(f"Roles: {roles}")
    print()

    print("Permissions:")

    print_permission_result(
        service,
        user,
        Permission(
            resource="knowledge",
            action="read",
        ),
    )

    print_permission_result(
        service,
        user,
        Permission(
            resource="knowledge",
            action="write",
        ),
    )

    print()
    print("Authorized Domains:")

    print_scope_result(
        service,
        user,
        (
            "employee_policies",
            "finance_policies",
        ),
        resource_type="domain",
    )

    print()
    print("Authorized Knowledge Bases:")

    print_scope_result(
        service,
        user,
        (
            "employee_kb",
            "finance_kb",
        ),
        resource_type="knowledge_base",
    )

    print()


def main() -> None:
    """Run the authorization smoke test."""

    service = create_authorization_service()

    users = (
        User(
            user_id="employee_user",
            roles=frozenset({"employee"}),
        ),
        User(
            user_id="finance_manager_user",
            roles=frozenset({"finance_manager"}),
        ),
        User(
            user_id="employee_finance_user",
            roles=frozenset(
                {
                    "employee",
                    "finance_manager",
                },
            ),
        ),
    )

    print()
    print("=" * 60)
    print("Authorization Framework Smoke Test")
    print("=" * 60)

    for user in users:
        print_user_test(service, user)

    print("=" * 60)
    print("Smoke test completed.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
