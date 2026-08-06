from sqlalchemy.orm import Session
from typing import Annotated

from fastapi import Depends
from backend.operations.providers.logging_provider import LoggingProvider

from backend.database.session import get_db
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

    tracker = OperationTracker(
        providers=[
            LoggingProvider(),
        ],
    )

    ingestion_service = DocumentIngestionService(
        tracker=tracker,
    )

    return UploadService(
        session=session,
        ingestion_service=ingestion_service,
    )
