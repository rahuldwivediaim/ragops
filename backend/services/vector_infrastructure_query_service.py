"""Service for querying configured vector infrastructure."""

from __future__ import annotations

from backend.models.vector_index import VectorIndex
from backend.repositories.vector_index_repository import VectorIndexRepository


class VectorInfrastructureQueryService:
    """Provide read-only access to vector infrastructure configuration."""

    def __init__(
        self,
        repository: VectorIndexRepository,
    ) -> None:
        self._repository = repository

    def get_active(self) -> list[VectorIndex]:
        """Return all active, non-deleted vector infrastructure records."""

        return self._repository.get_active()