"""
Configuration Loader

Public entry point for loading application configuration.

This module intentionally contains very little logic. The heavy lifting
is delegated to ConfigurationManager.

Author: Enterprise AI Platform
"""

from __future__ import annotations

from pathlib import Path

from .manager import ConfigurationManager
from .settings import ApplicationSettings

# Singleton manager instance
_manager = ConfigurationManager()


def load_settings(
    *,
    yaml_file: str | Path | None = None,
    json_file: str | Path | None = None,
    dotenv_file: str | Path | None = None,
    env_prefix: str | None = None,
    reload: bool = False,
) -> ApplicationSettings:
    """
    Load application settings.

    Parameters
    ----------
    yaml_file
        Optional YAML configuration file.

    json_file
        Optional JSON configuration file.

    dotenv_file
        Optional .env file.

    env_prefix
        Optional environment variable prefix.

    reload
        Forces configuration to be reloaded.

    Returns
    -------
    ApplicationSettings
    """

    if reload:
        _manager.clear_cache()

    resolved_env_prefix = env_prefix if env_prefix is not None else "RAGOPS_"

    return _manager.load(
        yaml_file=yaml_file,
        json_file=json_file,
        dotenv_file=dotenv_file,
        env_prefix=resolved_env_prefix,
    )

    return _manager.settings


def reload_settings() -> ApplicationSettings:
    """
    Reload configuration from all configured sources.
    """

    _manager.clear_cache()
    return _manager.settings


def get_settings() -> ApplicationSettings:
    """
    Return cached application settings.
    """

    return _manager.settings


__all__ = [
    "load_settings",
    "reload_settings",
    "get_settings",
]
