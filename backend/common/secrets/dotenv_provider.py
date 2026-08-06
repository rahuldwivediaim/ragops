"""
File:
    backend/common/secrets/dotenv_provider.py

Purpose:
    Secret provider backed by a .env file.

Description:
    Uses python-dotenv to load secrets from the project's .env file.

Responsibilities:
    - Load .env once.
    - Retrieve secrets by key.
    - Never raise an exception for missing secrets.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from backend.common.secrets.base import BaseSecretProvider


class DotEnvSecretProvider(BaseSecretProvider):
    """Secret provider that reads values from a .env file."""

    def __init__(
        self,
        env_file: Path | None = None,
    ) -> None:
        if env_file is None:
            project_root = Path(__file__).resolve().parents[3]
            env_file = project_root / ".env"

        load_dotenv(env_file, override=False)

    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        """
        Retrieve a secret from the .env file.

        Parameters
        ----------
        key:
            Secret name.

        default:
            Default value if the secret does not exist.
        """
        return os.getenv(key, default)
