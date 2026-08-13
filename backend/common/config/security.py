"""
backend/common/config/security.py
"""

from __future__ import annotations

from pydantic import Field

from .base import BaseConfig

from .authorization import (
    AccessPolicyConfig,
    DevelopmentUserConfig,
    PermissionConfig,
    RoleConfig,
)


class JWTConfig(BaseConfig):
    algorithm: str = "HS256"
    access_token_expiry_minutes: int = Field(default=60, ge=1)
    refresh_token_expiry_days: int = Field(default=30, ge=1)


class APIKeyConfig(BaseConfig):
    enabled: bool = True
    header_name: str = "X-API-Key"


class CORSConfig(BaseConfig):
    enabled: bool = True
    allow_origins: list[str] = Field(default_factory=lambda: ["*"])
    allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    allow_headers: list[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = True


class CookieConfig(BaseConfig):
    secure: bool = True
    http_only: bool = True
    same_site: str = "lax"
    domain: str | None = None


class EncryptionConfig(BaseConfig):
    enabled: bool = True
    algorithm: str = "AES-256-GCM"


class AuthenticationConfig(BaseConfig):
    enabled: bool = True
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    api_key: APIKeyConfig = Field(default_factory=APIKeyConfig)
    cookies: CookieConfig = Field(default_factory=CookieConfig)


class AuthorizationConfig(BaseConfig):
    """Application authorization configuration."""

    enabled: bool = True
    rbac: bool = True
    default_role: str = "user"

    permissions: dict[str, PermissionConfig] = Field(default_factory=dict)
    roles: dict[str, RoleConfig] = Field(default_factory=dict)
    policies: dict[str, AccessPolicyConfig] = Field(default_factory=dict)
    development_users: dict[str, DevelopmentUserConfig] = Field(
        default_factory=dict,
    )


__all__ = [
    "APIKeyConfig",
    "AuthenticationConfig",
    "AuthorizationConfig",
    "CORSConfig",
    "CookieConfig",
    "EncryptionConfig",
    "JWTConfig",
]
