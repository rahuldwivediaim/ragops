"""
File:
    backend/common/secrets/base.py

Purpose:
    Defines the abstraction for secret providers.

Description:
    Secret providers retrieve sensitive values such as
    API keys, passwords and tokens.

Implementations may retrieve secrets from:

- .env
- Azure Key Vault
- AWS Secrets Manager
- Hashicorp Vault

Business services should depend only on this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseSecretProvider(ABC):
    """Abstract secret provider."""

    @abstractmethod
    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        """
        Retrieve a secret.

        Parameters
        ----------
        key:
            Secret name.

        default:
            Returned if the secret is missing.
        """
        raise NotImplementedError
