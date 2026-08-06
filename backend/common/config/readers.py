"""
Configuration readers.

Provides reader implementations for supported configuration sources.
Each reader is responsible only for reading configuration and returning
a dictionary representation.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml


class ConfigReader(ABC):
    """
    Base class for all configuration readers.
    """

    @abstractmethod
    def read(self) -> dict[str, Any]:
        """
        Read configuration from the configured source.

        Returns
        -------
        dict[str, Any]
        """
        raise NotImplementedError


class JsonReader(ConfigReader):
    """
    Reads configuration from a JSON file.
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def read(self) -> dict[str, Any]:
        with self.file_path.open("r", encoding="utf-8") as file:
            return json.load(file)


class YamlReader(ConfigReader):
    """
    Reads configuration from a YAML file.
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def read(self) -> dict[str, Any]:
        with self.file_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}


class EnvironmentReader(ConfigReader):
    """
    Reads operating system environment variables.
    """

    def __init__(self, prefix: str | None = None):
        self.prefix = prefix

    def read(self) -> dict[str, Any]:
        if self.prefix is None:
            return dict(os.environ)

        prefix = self.prefix.upper()

        return {
            key[len(prefix) :]: value
            for key, value in os.environ.items()
            if key.upper().startswith(prefix)
        }


class DotEnvReader(ConfigReader):
    """
    Reads configuration values from a .env file.

    Supported format
    ----------------
    RAGOPS_STORAGE__PROVIDER=LOCAL

    RAGOPS_AUTHENTICATION__JWT__SECRET_KEY=xxxx

    Nested keys are separated using "__".
    """

    def __init__(
        self,
        file_path: str | Path,
        prefix: str = "RAGOPS_",
    ) -> None:
        self.file_path = Path(file_path)
        self.prefix = prefix.upper()

    def _set_nested(
        self,
        data: dict[str, Any],
        key: str,
        value: str,
    ) -> None:
        """
        Store a value inside a nested dictionary.

        Example
        -------
        AUTHENTICATION__JWT__SECRET_KEY

        becomes

        {
            "authentication": {
                "jwt": {
                    "secret_key": value
                }
            }
        }
        """

        parts = key.lower().split("__")

        current = data

        for part in parts[:-1]:
            current = current.setdefault(part, {})

        current[parts[-1]] = value

    def read(self) -> dict[str, Any]:
        values: dict[str, Any] = {}

        if not self.file_path.exists():
            return values

        with self.file_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split("=", 1)

                key = key.strip()

                if not key.upper().startswith(self.prefix):
                    continue

                key = key[len(self.prefix) :]

                self._set_nested(
                    values,
                    key,
                    value.strip(),
                )

        return values


__all__ = [
    "ConfigReader",
    "JsonReader",
    "YamlReader",
    "EnvironmentReader",
    "DotEnvReader",
]
