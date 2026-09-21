"""
Document ingestion service.

This service orchestrates the complete document ingestion workflow.

Workflow
--------
1. Build processing context
2. Execute validation / parsing / chunking pipeline
3. Persist parsing metadata
4. Persist chunks
5. Generate embeddings
6. Write vectors to Pinecone
7. Persist embedding metadata
8. Complete operation tracking

The service deliberately does not contain provider-specific implementation.
Embedding and vector-store work is delegated to
IngestionPersistenceService.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from uuid import UUID

from backend.document_processing.pipeline import (
    ProcessingContext,
    ProcessingPipeline,
)
from backend.operations.enums import OperationType
from backend.operations.tracker import OperationTracker
from backend.repositories.document_parsing_metadata_repository import (
    DocumentParsingMetadataRepository,
)
from backend.services.ingestion_persistence_service import (
    IngestionPersistenceService,
)
from backend.services.processing_job_service import ProcessingJobService

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """
    Orchestrates document processing and persistence.

    Responsibilities
    ----------------
    - Validate the source through the processing pipeline.
    - Parse the document.
    - Chunk the document.
    - Persist parsing metadata.
    - Delegate embeddings/vector indexing/persistence.
    - Track operation success/failure.
    """

    def __init__(
        self,
        *,
        tracker: OperationTracker,
        pipeline: ProcessingPipeline,
        parsing_metadata_repository: DocumentParsingMetadataRepository,
        persistence_service: IngestionPersistenceService,
        processing_job_service: ProcessingJobService,
    ) -> None:
        self._tracker = tracker
        self._pipeline = pipeline
        self._parsing_metadata_repository = parsing_metadata_repository
        self._persistence_service = persistence_service
        self._processing_job_service = processing_job_service

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest(
        self,
        *,
        source: str | Path,
        document_id: UUID,
        document_version_id: UUID,
        knowledge_base_id: UUID,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Ingest a document.

        Parameters
        ----------
        source:
            Absolute path to the stored document.

        document_id:
            Persistent Document identifier.

        document_version_id:
            Persistent DocumentVersion identifier.

        knowledge_base_id:
            Owning Knowledge Base identifier.

        metadata:
            Optional ingestion metadata.

        Returns
        -------
        Ingestion
            Persisted and indexed ingestion record.
        """

        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(
                f"Document source does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Document source is not a file: {path}"
            )

        operation_context = self._tracker.start(
            operation_type=OperationType.DOCUMENT_INGESTION,
            resource_name=path.name,
            metadata=metadata or {},
        )

        ingestion = None

        try:
            logger.info(
                "Starting document ingestion.",
                extra={
                    "document_id": str(document_id),
                    "document_version_id": str(document_version_id),
                    "knowledge_base_id": str(knowledge_base_id),
                    "source": str(path),
                },
            )

            # ----------------------------------------------------------
            # Initialize the durable ingestion execution record
            # ----------------------------------------------------------

            # The ingestion record must exist before the first processing
            # stage executes so that every stage, processing job and pipeline
            # event can reference the same durable execution identifier.
            ingestion = self._persistence_service.create_ingestion(
                document_version_id=document_version_id,
                trigger_source="UPLOAD",
            )

            processing_context = ProcessingContext(
                document_id=document_id,
                document_version_id=document_version_id,
                knowledge_base_id=knowledge_base_id,
                source_file=path,
            )

            if metadata:
                processing_context.metadata.update(metadata)

            processing_context.metadata["ingestion_id"] = str(ingestion.id)

            # ----------------------------------------------------------
            # Processing pipeline
            # ----------------------------------------------------------

            result = self._pipeline.execute(
                processing_context,
                observer=self._processing_job_service,
            )

            if result.failed:
                if result.exception is not None:
                    raise result.exception

                raise RuntimeError(
                    "Document processing failed without an exception."
                )

            if not processing_context.chunks:
                raise ValueError(
                    "Document processing completed but produced no chunks."
                )

            logger.info(
                "Document processing completed.",
                extra={
                    "document_id": str(document_id),
                    "document_version_id": str(document_version_id),
                    "chunk_count": processing_context.chunk_count,
                },
            )

            # ----------------------------------------------------------
            # Parsing metadata
            # ----------------------------------------------------------

            if processing_context.parsing_metadata is not None:
                existing_parsing_metadata = (
                    self._parsing_metadata_repository.get_by_document_version(
                        document_version_id,
                        )
                )

            if existing_parsing_metadata is None:
                self._parsing_metadata_repository.create(
                    processing_context.parsing_metadata,
                )
                logger.info(
                    "Parsing metadata created.",
                    extra={
                        "document_version_id": str(document_version_id),
                    },
                )
            else:
                logger.info(
                    "Parsing metadata already exists; reusing existing record.",
                    extra={
                        "document_version_id": str(document_version_id),
                        "parsing_metadata_id": str(existing_parsing_metadata.id),
                    },
            )
            # ----------------------------------------------------------
            # Persistence / embeddings / vector indexing
            # ----------------------------------------------------------

            ingestion = self._persistence_service.persist(
                ingestion=ingestion,
                document_id=document_id,
                document_version_id=document_version_id,
                knowledge_base_id=knowledge_base_id,
                source_filename=path.name,
                chunks=processing_context.chunks,
                metadata=processing_context.metadata,
                processing_job_service=self._processing_job_service,
            )

            # ----------------------------------------------------------
            # Operation tracking
            # ----------------------------------------------------------

            self._tracker.complete(
                operation_context,
            )

            logger.info(
                "Document ingestion completed successfully.",
                extra={
                    "document_id": str(document_id),
                    "document_version_id": str(document_version_id),
                    "ingestion_id": str(ingestion.id),
                    "chunk_count": ingestion.total_chunks,
                    "embedding_count": ingestion.total_embeddings,
                    "vector_count": ingestion.total_vectors_written,
                },
            )

            return ingestion

        except Exception as ex:
            logger.exception(
                "Document ingestion failed.",
                extra={
                    "document_id": str(document_id),
                    "document_version_id": str(document_version_id),
                    "source": str(path),
                },
            )

            if ingestion is not None:
                self._persistence_service.mark_failed(
                    ingestion=ingestion,
                    exception=ex,
                )

            self._tracker.fail(
                context=operation_context,
                exception=ex,
            )

            raise

        finally:
            self._processing_job_service.close()


__all__ = [
    "DocumentIngestionService",
]