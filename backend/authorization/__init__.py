"""
Authorization framework.

Provides authentication-independent authorization contracts
for users, roles, permissions and authorization decisions.
"""

from .models import (
    AccessScope,
    AuthorizationDecision,
    Decision,
    Permission,
    Role,
    User,
)
from .registry import (
    AccessPolicyRegistry,
    RoleRegistry,
)
from .service import AuthorizationService

__all__ = [
    "AccessPolicyRegistry",
    "AccessScope",
    "AuthorizationDecision",
    "AuthorizationService",
    "Decision",
    "Permission",
    "Role",
    "RoleRegistry",
    "User",
]
