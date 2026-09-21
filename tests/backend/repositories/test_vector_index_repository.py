
"""Tests for VectorIndexRepository."""

from unittest.mock import MagicMock

from backend.models.vector_index import VectorIndex
from backend.repositories.vector_index_repository import VectorIndexRepository


def _create_repository() -> tuple[VectorIndexRepository, MagicMock]:
    """Create a repository with a mocked SQLAlchemy session."""

    session = MagicMock()
    repository = VectorIndexRepository(session)

    return repository, session


def test_repository_uses_vector_index_model() -> None:
    """Repository should be configured with the VectorIndex model."""

    repository, _ = _create_repository()

    assert repository._model is VectorIndex


def test_get_active_returns_vector_indexes() -> None:
    """get_active should return active, non-deleted vector indexes."""

    repository, session = _create_repository()

    expected_indexes = [
        MagicMock(spec=VectorIndex),
        MagicMock(spec=VectorIndex),
    ]

    session.scalars.return_value.all.return_value = expected_indexes

    result = repository.get_active()

    assert result == expected_indexes
    session.scalars.assert_called_once()


def test_get_active_returns_empty_list_when_no_indexes_exist() -> None:
    """get_active should return an empty list when no records exist."""

    repository, session = _create_repository()

    session.scalars.return_value.all.return_value = []

    result = repository.get_active()

    assert result == []
    session.scalars.assert_called_once()