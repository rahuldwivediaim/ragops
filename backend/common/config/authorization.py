"""
Authorization configuration models.

Defines the configuration contract for roles, permissions,
access policies, and development users.
"""

from __future__ import annotations

from pydantic import Field

from .base import BaseConfig


class PermissionConfig(BaseConfig):
    """Configuration for a named authorization permission."""

    action: str = Field(min_length=1)


class RoleConfig(BaseConfig):
    """Configuration for an atomic authorization role."""

    permissions: tuple[str, ...] = ()
    policies: tuple[str, ...] = ()


class AccessPolicyConfig(BaseConfig):
    """Configuration defining the access scope granted by a policy."""

    domains: tuple[str, ...] = ()
    knowledge_bases: tuple[str, ...] = ()


class DevelopmentUserConfig(BaseConfig):
    """Configuration for a development/test user."""

    roles: tuple[str, ...] = ()


__all__ = [
    "AccessPolicyConfig",
    "DevelopmentUserConfig",
    "PermissionConfig",
    "RoleConfig",
]
