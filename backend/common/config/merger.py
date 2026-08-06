"""
backend/common/config/merger.py

Configuration merge utilities.

Provides immutable, recursive dictionary merge operations used by the
configuration framework.

Author: RAGOps Platform
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def deep_merge(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    """
    Recursively merge two dictionaries.

    Rules
    -----
    1. Nested dictionaries are merged recursively.
    2. Values from 'override' take precedence.
    3. Neither input dictionary is modified.
    4. Lists are replaced (not merged).

    Parameters
    ----------
    base:
        Base configuration.

    override:
        Configuration overriding base values.

    Returns
    -------
    dict[str, Any]
        New merged dictionary.

    Example
    -------
    >>> base = {"a": 1, "db": {"host": "localhost", "port": 5432}}
    >>> override = {"db": {"host": "prod"}}
    >>> deep_merge(base, override)
    {
        "a": 1,
        "db": {
            "host": "prod",
            "port": 5432
        }
    }
    """

    result = deepcopy(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def merge_many(*configs: dict[str, Any]) -> dict[str, Any]:
    """
    Merge multiple configuration dictionaries.

    Configuration precedence follows argument order:

        config1
            <- config2
                <- config3
                    <- ...

    The last configuration wins.

    Parameters
    ----------
    *configs:
        Configuration dictionaries.

    Returns
    -------
    dict[str, Any]
        Merged configuration.
    """

    merged: dict[str, Any] = {}

    for config in configs:
        merged = deep_merge(merged, config)

    return merged


__all__ = [
    "deep_merge",
    "merge_many",
]
