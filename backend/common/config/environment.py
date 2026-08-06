"""
backend/common/config/environment.py

Environment detection and helpers.
"""

from __future__ import annotations

import os
from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


_ENV_ALIASES = {
    "dev": Environment.DEVELOPMENT,
    "development": Environment.DEVELOPMENT,
    "local": Environment.DEVELOPMENT,
    "test": Environment.TEST,
    "testing": Environment.TEST,
    "stage": Environment.STAGING,
    "staging": Environment.STAGING,
    "prod": Environment.PRODUCTION,
    "production": Environment.PRODUCTION,
}


def get_environment(env_var: str = "APP_ENV") -> Environment:
    """Return the current application environment."""
    value = os.getenv(env_var, "development").strip().lower()
    return _ENV_ALIASES.get(value, Environment.DEVELOPMENT)


def is_development() -> bool:
    return get_environment() is Environment.DEVELOPMENT


def is_test() -> bool:
    return get_environment() is Environment.TEST


def is_staging() -> bool:
    return get_environment() is Environment.STAGING


def is_production() -> bool:
    return get_environment() is Environment.PRODUCTION


__all__ = [
    "Environment",
    "get_environment",
    "is_development",
    "is_test",
    "is_staging",
    "is_production",
]
