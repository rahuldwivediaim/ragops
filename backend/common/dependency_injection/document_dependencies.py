"""
FastAPI dependency providers for document services.

Builds the dependency graph required for document upload and ingestion.

Dependency graph
----------------

    UploadService
        |
        v
    DocumentIngestionService
        |
        +--> ProcessingPipeline
        |
        +--> DocumentParsingMetadataRepository
        |
        +--> IngestionPersistenceService
                |
                +--> EmbeddingProvider
                |
                +--> PineconeProvider

Provider configuration comes from application settings.

Provider credentials are loaded from environment variables:
    OPENAI_API_KEY
    PINECONE_API_KEY
"""

from __future__ import annotations

import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.common.config.loader import load_settings
from backend.database.session import SessionLocal, get_db
from backend.document_processing.chunker import TextChunker
from backend.document_processing.pipeline import ProcessingPipeline
from backend.document_processing.stages.chunking_stage import ChunkingStage
from backend.document_processing.stages.parsing_stage import ParsingStage
from backend.document_processing.stages.validation_stage import ValidationStage
from backend.embeddings.providers.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from backend.embeddings.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)
from backend.operations.providers.logging_provider import LoggingProvider
from backend.operations.tracker import OperationTracker
from backend.repositories.document_parsing_metadata_repository import (
    DocumentParsingMetadataRepository,
)
from backend.services.document_ingestion_service import (
    DocumentIngestionService,
)
from backend.services.documents.upload_service import UploadService
from backend.services.ingestion_persistence_service import (
    IngestionPersistenceService,
)
from backend.repositories.pipeline_event_repository import PipelineEventRepository
from backend.repositories.processing_job_repository import ProcessingJobRepository
from backend.services.pipeline_event_service import PipelineEventService
from backend.services.processing_job_service import ProcessingJobService
from backend.vector_store.providers.pinecone_provider import (
    PineconeProvider,
)


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------------------------
# Provider builders
# ---------------------------------------------------------------------------


def _build_embedding_provider(
    settings,
) -> BaseEmbeddingProvider:
    """
    Build the configured embedding provider.

    Provider configuration comes from application settings.

    Credentials come from the environment:
        OPENAI_API_KEY

    The current document-ingestion E2E path supports OpenAI.
    """

    if not settings.embeddings.enabled:
        raise RuntimeError(
            "Embedding provider is disabled in application configuration."
        )

    provider = settings.embeddings.provider.value

    if provider != "openai":
        raise RuntimeError(
            "The current document-ingestion E2E path supports only "
            "the OpenAI embedding provider. "
            f"Configured provider: {provider!r}"
        )

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAIEmbeddingProvider(
        api_key=api_key,
        model_name=settings.embeddings.model,
        dimensions=settings.embeddings.dimensions,
    )


def _build_vector_store(
    settings,
) -> PineconeProvider:
    """
    Build the configured Pinecone vector store.

    Provider configuration comes from application settings.

    Credentials come from the environment:
        PINECONE_API_KEY
    """

    if not settings.vector_store.enabled:
        raise RuntimeError(
            "Vector store is disabled in application configuration."
        )

    provider = settings.vector_store.provider.value

    if provider != "pinecone":
        raise RuntimeError(
            "The current document-ingestion E2E path requires Pinecone. "
            f"Configured vector store: {provider!r}. "
            "Update config/application.yaml before starting ingestion."
        )

    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "PINECONE_API_KEY is not configured."
        )

    if not settings.vector_store.index_name:
        raise RuntimeError(
            "Pinecone index name is not configured."
        )

    if not settings.vector_store.namespace:
        raise RuntimeError(
            "Pinecone namespace is not configured."
        )

    return PineconeProvider(
        api_key=api_key,
        index_name=settings.vector_store.index_name,
        namespace=settings.vector_store.namespace,
    )


# ---------------------------------------------------------------------------
# Document upload dependency
# ---------------------------------------------------------------------------


def get_document_upload_service(
    session: Annotated[Session, Depends(get_db)],
) -> UploadService:
    """
    Dependency provider for UploadService.

    Complete dependency graph:

        UploadService
            |
            v
        DocumentIngestionService
            |
            +--> ProcessingPipeline
            |
            +--> DocumentParsingMetadataRepository
            |
            +--> IngestionPersistenceService
                    |
                    +--> EmbeddingProvider
                    |
                    +--> PineconeProvider
    """

    settings = load_settings()

    # ------------------------------------------------------------------
    # Operation tracking
    # ------------------------------------------------------------------

    tracker = OperationTracker(
        providers=[
            LoggingProvider(),
        ],
    )

    # ------------------------------------------------------------------
    # Document chunker
    # ------------------------------------------------------------------

    chunker = TextChunker()

    # ------------------------------------------------------------------
    # Document processing pipeline
    # ------------------------------------------------------------------

    pipeline = ProcessingPipeline()

    pipeline.add_stage(
        ValidationStage(),
    )

    pipeline.add_stage(
        ParsingStage(),
    )

    pipeline.add_stage(
        ChunkingStage(
            chunker=chunker,
        ),
    )

    # ------------------------------------------------------------------
    # Parsing metadata repository
    # ------------------------------------------------------------------

    parsing_metadata_repository = DocumentParsingMetadataRepository(
        session=session,
    )

    # ------------------------------------------------------------------
    # Embedding provider
    # ------------------------------------------------------------------

    embedding_provider = _build_embedding_provider(
        settings,
    )

    # ------------------------------------------------------------------
    # Vector store
    # ------------------------------------------------------------------

    vector_store = _build_vector_store(
        settings,
    )

    # ------------------------------------------------------------------
    # Ingestion persistence
    # ------------------------------------------------------------------

    # Keep observability commits isolated from the main ingestion transaction.
    processing_job_session = SessionLocal()
    processing_job_repository = ProcessingJobRepository(
        session=processing_job_session,
    )

    pipeline_event_session = SessionLocal()
    pipeline_event_repository = PipelineEventRepository(
        session=pipeline_event_session,
    )
    pipeline_event_service = PipelineEventService(
        pipeline_event_repository,
    )

    processing_job_service = ProcessingJobService(
        processing_job_repository,
        event_service=pipeline_event_service,
    )

    persistence_service = IngestionPersistenceService(
        session=session,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    # ------------------------------------------------------------------
    # Document ingestion service
    # ------------------------------------------------------------------

    ingestion_service = DocumentIngestionService(
        tracker=tracker,
        pipeline=pipeline,
        parsing_metadata_repository=parsing_metadata_repository,
        persistence_service=persistence_service,
        processing_job_service=processing_job_service,
    )

    # ------------------------------------------------------------------
    # Upload service
    # ------------------------------------------------------------------

    return UploadService(
        session=session,
        ingestion_service=ingestion_service,
    )


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "get_document_upload_service",
]