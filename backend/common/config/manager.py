"""
Configuration Manager

Coordinates configuration loading by orchestrating readers,
merge operations and settings construction.

Loading Order (lowest → highest priority)

1. config/application.yaml
2. .env
3. Operating System Environment Variables

Future enhancement
------------------
Environment-specific configuration files (development.yaml,
test.yaml, production.yaml) will be inserted between
application.yaml and .env.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .merger import merge_many
from .readers import (
    DotEnvReader,
    EnvironmentReader,
    JsonReader,
    YamlReader,
)
from .settings import ApplicationSettings


class ConfigurationManager:
    """
    Central configuration orchestrator.

    Responsible for

    - Reading configuration
    - Merging configuration
    - Building ApplicationSettings
    - Caching settings
    """

    def __init__(self) -> None:
        self._settings: ApplicationSettings | None = None

    @property
    def settings(self) -> ApplicationSettings:
        """
        Return cached settings.

        Loads configuration lazily on first access.
        """

        if self._settings is None:
            self._settings = self.load()

        return self._settings

    def clear_cache(self) -> None:
        """Clear cached settings."""

        self._settings = None

    def load(
        self,
        *,
        yaml_file: str | Path | None = None,
        json_file: str | Path | None = None,
        dotenv_file: str | Path | None = None,
        env_prefix: str = "RAGOPS_",
    ) -> ApplicationSettings:
        """
        Load application configuration.

        Parameters
        ----------
        yaml_file
            Optional YAML configuration file.
            Defaults to config/application.yaml.

        json_file
            Optional JSON configuration file.

        dotenv_file
            Optional .env file.
            Defaults to .env in the project root.

        env_prefix
            Prefix used for environment variables.
        """

        project_root = Path(__file__).resolve().parents[3]

        if yaml_file is None:
            yaml_file = project_root / "config" / "application.yaml"

        if dotenv_file is None:
            dotenv_file = project_root / ".env"

        configs: list[dict[str, Any]] = []

        yaml_path = Path(yaml_file)
        if yaml_path.exists():
            configs.append(YamlReader(yaml_path).read())

        if json_file:
            json_path = Path(json_file)
            if json_path.exists():
                configs.append(JsonReader(json_path).read())

        dotenv_path = Path(dotenv_file)
        if dotenv_path.exists():
            configs.append(DotEnvReader(dotenv_path).read())

        #
        # Only read environment variables beginning with RAGOPS_
        #
        configs.append(EnvironmentReader(env_prefix).read())

        merged = merge_many(*configs)

        return ApplicationSettings.model_validate(merged)


# ----------------------------------------------------------------------
# Global Configuration Manager
# ----------------------------------------------------------------------

configuration_manager = ConfigurationManager()

settings = configuration_manager.settings


__all__ = [
    "ConfigurationManager",
    "configuration_manager",
    "settings",
]
