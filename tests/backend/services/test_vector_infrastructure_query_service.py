"""Tests for VectorInfrastructureQueryService."""

from unittest.mock import MagicMock

from backend.models.vector_index import VectorIndex
from backend.repositories.vector_index_repository import VectorIndexRepository
from backend.services.vector_infrastructure_query_service import (
    VectorInfrastructureQueryService,
)


def _create_service() -> tuple[
    VectorInfrastructureQueryService,
    MagicMock,
]:
    """Create a service with a mocked repository."""

    repository = MagicMock(spec=VectorIndexRepository)
    service = VectorInfrastructureQueryService(repository)

    return service, repository


def test_get_active_returns_vector_indexes() -> None:
    """Service should return active vector infrastructure records."""

    service, repository = _create_service()

    expected_indexes = [
        MagicMock(spec=VectorIndex),
        MagicMock(spec=VectorIndex),
    ]
    repository.get_active.return_value = expected_indexes

    result = service.get_active()

    assert result == expected_indexes
    repository.get_active.assert_called_once_with()


def test_get_active_returns_empty_list_when_no_indexes_exist() -> None:
    """Service should return an empty list when no indexes exist."""

    service, repository = _create_service()

    repository.get_active.return_value = []

    result = service.get_active()

    assert result == []
    repository.get_active.assert_called_once_with()