"""
File:
    backend/repositories/base_repository.py

Purpose:
    Generic repository providing common CRUD operations for SQLAlchemy models.
"""

from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository for SQLAlchemy models."""

    def __init__(
        self,
        session: Session,
        model: type[ModelType],
    ) -> None:
        self._session = session
        self._model = model

    def create(
        self,
        entity: ModelType,
    ) -> ModelType:
        """Create a new entity."""

        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return entity

    def update(
        self,
        entity: ModelType,
    ) -> ModelType:
        """Update an existing entity."""

        self._session.commit()
        self._session.refresh(entity)
        return entity

    def delete(
        self,
        entity: ModelType,
    ) -> None:
        """Delete an entity."""

        self._session.delete(entity)
        self._session.commit()

    def get_by_id(
        self,
        entity_id: UUID,
    ) -> ModelType | None:
        """Return an entity by its ID."""

        return self._session.get(
            self._model,
            entity_id,
        )

    def get_by_id_or_raise(
        self,
        entity_id: UUID,
        message: str | None = None,
    ) -> ModelType:
        """
        Return an entity by ID.

        Raises:
            ValueError: If the entity does not exist.
        """

        entity = self.get_by_id(entity_id)

        if entity is None:
            raise ValueError(message or f"{self._model.__name__} not found.")

        return entity

    def get_all(
        self,
    ) -> list[ModelType]:
        """Return all entities."""

        statement = select(self._model)

        return list(self._session.scalars(statement).all())

    def exists(
        self,
        entity_id: UUID,
    ) -> bool:
        """Check whether an entity exists."""

        return self.get_by_id(entity_id) is not None
