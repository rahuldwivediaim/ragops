"""
File:
    backend/common/secrets/manager.py

Purpose:
    Central access point for application secrets.

Description:
    SecretManager delegates secret retrieval to the configured
    secret provider. The rest of the application interacts only
    with this class and remains independent of the underlying
    secret storage implementation.

Current Provider
----------------
- DotEnvSecretProvider

Future Providers
----------------
- Azure Key Vault
- AWS Secrets Manager
- HashiCorp Vault
"""

from __future__ import annotations

from backend.common.secrets.base import BaseSecretProvider
from backend.common.secrets.dotenv_provider import DotEnvSecretProvider


class SecretManager:
    """
    Central manager for retrieving application secrets.
    """

    def __init__(
        self,
        provider: BaseSecretProvider | None = None,
    ) -> None:
        self._provider = provider or DotEnvSecretProvider()

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
            Value returned when the secret does not exist.

        Returns
        -------
        str | None
            Secret value.
        """
        return self._provider.get(
            key=key,
            default=default,
        )

    def require(
        self,
        key: str,
    ) -> str:
        """
        Retrieve a required secret.

        Raises
        ------
        RuntimeError
            If the secret is missing or empty.
        """
        value = self.get(key)

        if value is None or value.strip() == "":
            raise RuntimeError(f"Required secret '{key}' is missing.")

        return value


#
# Application-wide singleton
#
secret_manager = SecretManager()
