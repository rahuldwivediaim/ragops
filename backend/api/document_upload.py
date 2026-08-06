"""
Document Upload API

REST endpoints for uploading documents into a Knowledge Base.

Author: RAGOps
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)

from backend.schemas.document_upload import (
    DocumentMetadata,
    DocumentUploadResponse,
)
from backend.services.documents.upload_service import (
    UploadService,
)
from backend.common.dependency_injection import (
    get_document_upload_service,
)

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Document Upload"],
)


@router.post(
    "/{knowledge_base_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a document into a Knowledge Base.",
)
async def upload_document(
    knowledge_base_id: UUID,
    file: Annotated[UploadFile, File(...)],
    title: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    tags: Annotated[list[str] | None, Form()] = None,
    upload_service: UploadService = Depends(
        get_document_upload_service,
    ),
) -> DocumentUploadResponse:
    """
    Upload a document.

    Workflow
    --------
    1. Receive multipart upload.
    2. Build metadata object.
    3. Delegate upload to service layer.
    4. Return upload response.
    """

    metadata = DocumentMetadata(
        title=title,
        description=description,
        tags=tags or [],
    )

    return upload_service.upload_document(
        knowledge_base_id=knowledge_base_id,
        upload_file=file,
        metadata=metadata,
    )
