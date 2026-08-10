"""
FastAPI dependency providers for document services.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.repositories.document_parsing_metadata_repository import (
    DocumentParsingMetadataRepository,
)
from backend.database.session import get_db
from backend.document_processing.chunker import TextChunker
from backend.document_processing.pipeline import ProcessingPipeline
from backend.document_processing.stages.chunking_stage import ChunkingStage
from backend.document_processing.stages.parsing_stage import ParsingStage
from backend.document_processing.stages.validation_stage import ValidationStage
from backend.operations.providers.logging_provider import LoggingProvider
from backend.operations.tracker import OperationTracker
from backend.services.document_ingestion_service import (
    DocumentIngestionService,
)
from backend.services.documents.upload_service import UploadService


def get_document_upload_service(
    session: Annotated[Session, Depends(get_db)],
) -> UploadService:
    """
    Dependency provider for UploadService.
    """

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

    pipeline.add_stage(ValidationStage())

    pipeline.add_stage(ParsingStage())

    pipeline.add_stage(
        ChunkingStage(
            chunker=chunker,
        )
    )

    # ------------------------------------------------------------------
    # Parsing metadata repository
    # ------------------------------------------------------------------

    parsing_metadata_repository = DocumentParsingMetadataRepository(
        session=session,
    )

    # ------------------------------------------------------------------
    # Document ingestion service
    # ------------------------------------------------------------------

    ingestion_service = DocumentIngestionService(
        tracker=tracker,
        pipeline=pipeline,
        parsing_metadata_repository=parsing_metadata_repository,
    )

    # ------------------------------------------------------------------
    # Upload service
    # ------------------------------------------------------------------

    return UploadService(
        session=session,
        ingestion_service=ingestion_service,
    )
