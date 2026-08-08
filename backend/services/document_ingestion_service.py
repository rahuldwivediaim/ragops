"""
Document ingestion service.

This service orchestrates the complete document ingestion workflow.

Workflow
--------
1. Build processing context
2. Execute processing pipeline
3. Persist processing metadata
4. Complete operation

Each step is intentionally isolated to make the pipeline
easy to extend and test.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.operations.enums import OperationType
from backend.operations.tracker import OperationTracker

from uuid import UUID

from backend.document_processing.pipeline import (
    ProcessingContext,
    ProcessingPipeline,
)
from backend.repositories.document_parsing_metadata_repository import (
    DocumentParsingMetadataRepository,
)


class DocumentIngestionService:
    """
    Orchestrates document ingestion.
    """

    def __init__(
        self,
        tracker: OperationTracker,
        pipeline: ProcessingPipeline,
        parsing_metadata_repository: DocumentParsingMetadataRepository,
    ) -> None:
        self._tracker = tracker
        self._pipeline = pipeline
        self._parsing_metadata_repository = parsing_metadata_repository

    def ingest(
        self,
        source: str | Path,
        document_id: UUID,
        document_version_id: UUID,
        knowledge_base_id: UUID,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Ingest a document.

        Parameters
        ----------
        source
            Document path.

        metadata
            Optional document metadata.
        """

        path = Path(source)

        context = self._tracker.start(
            operation_type=OperationType.DOCUMENT_INGESTION,
            resource_name=path.name,
        )

        context.metadata.update(metadata or {})

        try:
            processing_context = ProcessingContext(
                document_id=document_id,
                document_version_id=document_version_id,
                knowledge_base_id=knowledge_base_id,
                source_file=path,
            )

            result = self._pipeline.execute(processing_context)

            if result.failed:
                raise result.exception

            if processing_context.parsing_metadata is not None:
                self._parsing_metadata_repository.add(
                    processing_context.parsing_metadata
                )

            self._tracker.complete(context)

        except Exception as ex:
            self._tracker.fail(
                context=context,
                exception=ex,
            )

            raise


__all__ = [
    "DocumentIngestionService",
]
