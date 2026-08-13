"""
Configuration Package

Provides the singleton ConfigurationManager instance for the application.

Purpose
-------
Every component in the application should obtain configuration through
this module rather than creating its own ConfigurationManager.

Example
-------
from backend.common.config import configuration

settings = configuration.settings
"""

from __future__ import annotations

from .domains import DomainConfig
from .manager import ConfigurationManager

configuration = ConfigurationManager()

__all__ = [
    "ConfigurationManager",
    "DomainConfig",
    "configuration",
]
