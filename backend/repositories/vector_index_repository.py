
"""Repository for vector infrastructure configuration."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.vector_index import VectorIndex
from backend.repositories.base_repository import BaseRepository


class VectorIndexRepository(BaseRepository[VectorIndex]):
    """Repository for vector infrastructure records."""

    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            model=VectorIndex,
        )

    def get_active(self) -> list[VectorIndex]:
        """Return active, non-deleted vector infrastructure records."""

        statement = (
            select(VectorIndex)
            .where(
                VectorIndex.is_active.is_(True),
                VectorIndex.deleted_at.is_(None),
            )
            .order_by(VectorIndex.name)
        )

        return list(self._session.scalars(statement).all())