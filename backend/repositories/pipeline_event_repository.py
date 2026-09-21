"""Repository for immutable ingestion pipeline events."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.enums import PipelineStage
from backend.models.pipeline_event import PipelineEvent
from backend.repositories.base_repository import BaseRepository


class PipelineEventRepository(BaseRepository[PipelineEvent]):
    """Persist append-only pipeline execution events."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, PipelineEvent)
        self._session = session

    def create_event(
        self,
        *,
        ingestion_id: UUID,
        stage: PipelineStage,
        event_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> PipelineEvent:
        """Create and commit one pipeline event."""

        event = PipelineEvent(
            ingestion_id=ingestion_id,
            stage=stage,
            event_type=event_type,
            message=message,
            details=json.dumps(details, default=str) if details else None,
        )
        return self.create(event)

    def close(self) -> None:
        """Close the dedicated event persistence session."""

        self._session.close()
