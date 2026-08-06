"""
Secrets Package

Provides centralized access to application secrets.

Business services should always import the singleton
SecretManager instance from this package.

Example
-------
from backend.common.secrets import secret_manager

api_key = secret_manager.require("OPENAI_API_KEY")
"""

from .base import BaseSecretProvider
from .dotenv_provider import DotEnvSecretProvider
from .manager import SecretManager, secret_manager

__all__ = [
    "BaseSecretProvider",
    "DotEnvSecretProvider",
    "SecretManager",
    "secret_manager",
]
