"""
Unit tests for configuration merge utilities.

Tests:
    - deep_merge()
    - merge_many()
"""

from copy import deepcopy

import pytest
from backend.common.config.merger import deep_merge, merge_many

# =============================================================================
# deep_merge()
# =============================================================================


@pytest.mark.unit
@pytest.mark.common
@pytest.mark.config
class TestDeepMerge:
    """Unit tests for deep_merge()."""

    def test_empty_dictionaries(self):
        """Merging two empty dictionaries returns an empty dictionary."""

        # Arrange
        base = {}
        override = {}

        # Act
        result = deep_merge(base, override)

        # Assert
        assert result == {}

    def test_flat_dictionary(self):
        """Override values should replace base values."""

        # Arrange
        base = {
            "host": "localhost",
            "port": 8000,
        }

        override = {
            "port": 9000,
        }

        # Act
        result = deep_merge(base, override)

        # Assert
        assert result == {
            "host": "localhost",
            "port": 9000,
        }

    def test_nested_dictionary(self):
        """Nested dictionaries should merge recursively."""

        # Arrange
        base = {
            "database": {
                "host": "localhost",
                "port": 5432,
            }
        }

        override = {
            "database": {
                "host": "production-db",
            }
        }

        # Act
        result = deep_merge(base, override)

        # Assert
        assert result == {
            "database": {
                "host": "production-db",
                "port": 5432,
            }
        }

    def test_is_immutable(self):
        """Input dictionaries must never be modified."""

        # Arrange
        base = {
            "database": {
                "host": "localhost",
            }
        }

        override = {
            "database": {
                "host": "prod",
            }
        }

        original_base = deepcopy(base)
        original_override = deepcopy(override)

        # Act
        deep_merge(base, override)

        # Assert
        assert base == original_base
        assert override == original_override

    def test_replaces_lists(self):
        """Lists should be replaced instead of merged."""

        # Arrange
        base = {
            "models": [
                "gpt-4",
                "gpt-4o",
            ]
        }

        override = {
            "models": [
                "gpt-5",
            ]
        }

        # Act
        result = deep_merge(base, override)

        # Assert
        assert result["models"] == ["gpt-5"]


# =============================================================================
# merge_many()
# =============================================================================


@pytest.mark.unit
@pytest.mark.common
@pytest.mark.config
class TestMergeMany:
    """Unit tests for merge_many()."""

    def test_respects_precedence(self):
        """Later configurations should override earlier ones."""

        # Arrange
        base = {
            "logging": {
                "level": "INFO",
            }
        }

        development = {
            "logging": {
                "level": "DEBUG",
            }
        }

        local = {
            "logging": {
                "level": "TRACE",
            }
        }

        # Act
        result = merge_many(base, development, local)

        # Assert
        assert result["logging"]["level"] == "TRACE"

    def test_empty(self):
        """Merging no configurations should return an empty dictionary."""

        # Act
        result = merge_many()

        # Assert
        assert result == {}
