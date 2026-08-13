"""
Authorization registries.
"""

from .access_policy_registry import AccessPolicyRegistry
from .role_registry import RoleRegistry

__all__ = [
    "AccessPolicyRegistry",
    "RoleRegistry",
]
