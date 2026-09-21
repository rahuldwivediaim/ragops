"""
Authorization service.

Evaluates authorization using authenticated users, configured roles,
permissions, and access policies.

This service is intentionally independent of authentication,
retrieval, vector databases, AI agents, and domain routing.
"""

from __future__ import annotations

from backend.authorization.models.access_scope import AccessScope
from backend.authorization.models.authorization_decision import (
    AuthorizationDecision,
    Decision,
)
from backend.authorization.models.permission import Permission
from backend.authorization.models.user import User
from backend.authorization.registry import (
    AccessPolicyRegistry,
    RoleRegistry,
)


class AuthorizationService:
    """
    Runtime authorization service.

    Responsibilities
    ----------------
    * Evaluate user permissions.
    * Resolve user roles.
    * Calculate effective access scope.
    * Combine access across multiple atomic roles.

    Non-responsibilities
    --------------------
    * Authentication.
    * Domain selection.
    * Document retrieval.
    * Vector database filtering.
    * AI-agent decisions.
    """

    def __init__(
        self,
        role_registry: RoleRegistry,
        access_policy_registry: AccessPolicyRegistry,
    ) -> None:
        self._role_registry = role_registry
        self._access_policy_registry = access_policy_registry

        self._validate_role_policy_references()

    def authorize_permission(
        self,
        user: User,
        permission: Permission,
    ) -> AuthorizationDecision:
        """
        Evaluate whether a user has a specific permission.

        Access is granted when any one of the user's roles contains
        the requested permission.

        Roles are additive. There is no primary-role concept.
        """

        for role_id in user.roles:
            role = self._role_registry.get(role_id)

            if role.has_permission(permission):
                return AuthorizationDecision(
                    decision=Decision.ALLOW,
                    reason=(
                        f"User '{user.user_id}' is authorized by "
                        f"role '{role_id}' for permission "
                        f"'{permission.key}'."
                    ),
                )

        return AuthorizationDecision(
            decision=Decision.DENY,
            reason=(
                f"User '{user.user_id}' does not have permission '{permission.key}'."
            ),
        )

    def has_permission(
        self,
        user: User,
        permission: Permission,
    ) -> bool:
        """Return whether a user has the specified permission."""

        return self.authorize_permission(
            user=user,
            permission=permission,
        ).allowed

    def get_access_scope(
        self,
        user: User,
    ) -> AccessScope:
        """
        Calculate the user's effective access scope.

        The effective scope is the union of all access policies
        referenced by all roles assigned to the user.

        Policy identifiers are retained because document-level
        authorization uses them to construct retrieval filters.
        """

        effective_scope = AccessScope()

        for role_id in user.roles:
            role = self._role_registry.get(role_id)

            for policy_id in role.policies:
                policy = self._access_policy_registry.get(
                    policy_id,
                )

                policy_scope = AccessScope(
                    domains=frozenset(policy.domains),
                    knowledge_bases=frozenset(
                        policy.knowledge_bases,
                    ),
                    access_policy_ids=frozenset(
                        {policy_id},
                    ),
                )

                effective_scope = effective_scope.union(
                    policy_scope,
                )

        return effective_scope

    def is_domain_authorized(
        self,
        user: User,
        domain_id: str,
    ) -> bool:
        """Return whether a user can access a specific domain."""

        return self.get_access_scope(user).includes_domain(
            domain_id,
        )

    def is_knowledge_base_authorized(
        self,
        user: User,
        knowledge_base_id: str,
    ) -> bool:
        """
        Return whether a user can access a specific knowledge base.
        """

        return self.get_access_scope(
            user,
        ).includes_knowledge_base(
            knowledge_base_id,
        )

    def is_policy_authorized(
        self,
        user: User,
        policy_id: str,
    ) -> bool:
        """
        Return whether a user has the specified access policy.
        """

        return self.get_access_scope(
            user,
        ).includes_policy(
            policy_id,
        )

    def _validate_role_policy_references(self) -> None:
        """
        Validate that all configured role policy references exist.

        Invalid authorization configuration should fail during
        service initialization rather than producing unpredictable
        authorization behavior at runtime.
        """

        for role_id in self._role_registry.list_ids():
            role = self._role_registry.get(role_id)

            for policy_id in role.policies:
                if not self._access_policy_registry.exists(
                    policy_id,
                ):
                    raise ValueError(
                        f"Role '{role_id}' references unknown "
                        f"authorization policy '{policy_id}'.",
                    )


__all__ = ["AuthorizationService"]
