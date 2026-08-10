"""
File:
    backend/services/document/upload_service.py

Purpose:
    Business service responsible for uploading documents into a
    Knowledge Base.

Responsibilities
----------------
- Validate upload requests.
- Store uploaded files.
- Create Document entities.
- Create DocumentVersion entities.
- Trigger document ingestion.

Notes
-----
This service is an orchestration layer only.

It delegates infrastructure work to:
    - UploadFileHelper
    - FileHash
    - DocumentTypeResolver
    - DocumentStorageService

It delegates persistence to repositories.

It delegates parsing/chunking/embedding to
DocumentIngestionService.
"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.common.resolvers.document_type_resolver import (
    DocumentTypeResolver,
)
from backend.common.utils.file_hash import FileHash
from backend.common.utils.upload_file_helper import (
    UploadFileHelper,
)
from backend.models.document import Document
from backend.models.enums import (
    DocumentSource,
    DocumentStatus,
)
from backend.models.document_version import (
    DocumentVersion,
)
from backend.repositories.document_repository import (
    DocumentRepository,
)
from backend.repositories.document_version_repository import (
    DocumentVersionRepository,
)
from backend.repositories.knowledge_base_repository import (
    KnowledgeBaseRepository,
)
from backend.schemas.document_upload import (
    DocumentMetadata,
    DocumentUploadResponse,
)
from backend.services.document_ingestion_service import (
    DocumentIngestionService,
)
from backend.storage.document_storage_service import (
    DocumentStorageService,
)

logger = logging.getLogger(__name__)


class UploadService:
    """
    Service responsible for uploading documents.
    """

    def __init__(
        self,
        session: Session,
        ingestion_service: DocumentIngestionService,
    ) -> None:
        self._session = session

        self._knowledge_base_repository = KnowledgeBaseRepository(session)

        self._document_repository = DocumentRepository(session)

        self._document_version_repository = DocumentVersionRepository(session)

        self._storage_service = DocumentStorageService()

        self._ingestion_service = ingestion_service

    # =========================================================================
    # Public API
    # =========================================================================

    def upload_document(
        self,
        *,
        knowledge_base_id: UUID,
        upload_file: UploadFile,
        metadata: DocumentMetadata,
    ) -> DocumentUploadResponse:
        """
        Upload a document into a Knowledge Base.
        """

        logger.info(
            "Starting document upload.",
            extra={
                "knowledge_base_id": str(knowledge_base_id),
                "filename": upload_file.filename,
            },
        )

        temporary_file: Path | None = None

        try:
            knowledge_base = self._validate_knowledge_base(knowledge_base_id)

            self._validate_upload(upload_file)

            temporary_file = self._save_temporary_file(upload_file)

            content_hash = self._compute_content_hash(temporary_file)

            self._check_duplicate(content_hash)

            stored_document = self._store_file(
                knowledge_base=knowledge_base,
                upload_file=upload_file,
                temporary_file=temporary_file,
            )

            document = self._build_document(
                knowledge_base=knowledge_base,
                upload_file=upload_file,
                metadata=metadata,
            )

            document = self._persist_document(document)

            version = self._build_document_version(
                document=document,
                upload_file=upload_file,
                stored_document=stored_document,
                content_hash=content_hash,
            )

            version = self._persist_document_version(version)

            self._trigger_ingestion(
                document=document,
                version=version,
                stored_document=stored_document,
            )

            return self._build_response(
                document=document,
                version=version,
                stored_document=stored_document,
                upload_file=upload_file,
            )

        finally:
            if temporary_file is not None:
                self._cleanup(temporary_file)

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_knowledge_base(
        self,
        knowledge_base_id: UUID,
    ):
        """
        Validate that the Knowledge Base exists.

        Returns
        -------
        KnowledgeBase
        """

        knowledge_base = self._knowledge_base_repository.get_by_id(knowledge_base_id)

        if knowledge_base is None:
            raise ValueError(f"Knowledge Base '{knowledge_base_id}' does not exist.")

        logger.debug(
            "Knowledge Base validated.",
            extra={
                "knowledge_base": knowledge_base.code,
            },
        )

        return knowledge_base

    def _get_filename(
        self,
        upload_file: UploadFile,
    ) -> str:
        """
        Return a validated upload filename.
        """

        filename = upload_file.filename

        if filename is None:
            raise ValueError("Uploaded filename cannot be empty.")

        if not filename.strip():
            raise ValueError("Uploaded filename cannot be empty.")

        return filename

    def _validate_upload(
        self,
        upload_file: UploadFile,
    ) -> None:
        """
        Validate uploaded document.
        """

        if upload_file.filename is None:
            raise ValueError("Uploaded filename cannot be empty.")

        if not upload_file.filename.strip():
            raise ValueError("Uploaded filename cannot be empty.")

        if not DocumentTypeResolver.is_supported(upload_file.filename):
            supported = ", ".join(DocumentTypeResolver.supported_extensions())

            raise ValueError(f"Unsupported document type. Supported types: {supported}")

        logger.debug(
            "Upload validated.",
            extra={
                "filename": upload_file.filename,
            },
        )

    def _check_duplicate(
        self,
        content_hash: str,
    ) -> None:
        """
        Check whether the uploaded content already exists.
        """

        print("=" * 80)
        print("CONTENT HASH :", content_hash)

        exists = self._document_version_repository.exists_by_hash(content_hash)

        print("EXISTS :", exists)
        print("=" * 80)

        if exists:
            raise ValueError("An identical document has already been uploaded.")

        #
        # Future Enhancement
        # ------------------
        # We may later allow duplicate uploads
        # into different Knowledge Bases.
        #

    # =========================================================================
    # Infrastructure
    # =========================================================================

    def _save_temporary_file(
        self,
        upload_file: UploadFile,
    ) -> Path:
        """
        Save the uploaded file to a temporary location.
        """

        temporary_file = UploadFileHelper.save_to_temp(upload_file)

        logger.debug(
            "Temporary file created.",
            extra={
                "path": str(temporary_file),
            },
        )

        return temporary_file

    def _compute_content_hash(
        self,
        temporary_file: Path,
    ) -> str:
        """
        Compute SHA-256 content hash.
        """

        content_hash = FileHash.sha256(temporary_file)

        logger.debug("Content hash computed.")

        return content_hash

    def _store_file(
        self,
        *,
        knowledge_base,
        upload_file: UploadFile,
        temporary_file: Path,
    ):
        """
        Store the uploaded document using the configured
        storage provider.
        """

        stored_document = self._storage_service.store_document(
            source_file=temporary_file,
            knowledge_base_code=knowledge_base.code,
            original_file_name=self._get_filename(upload_file),
            version_number=1,
        )

        logger.info(
            "Document stored successfully.",
            extra={
                "storage_path": stored_document.relative_path,
            },
        )

        return stored_document

    def _cleanup(
        self,
        temporary_file: Path,
    ) -> None:
        """
        Delete temporary upload file.
        """

        UploadFileHelper.cleanup(temporary_file)

        logger.debug(
            "Temporary file removed.",
            extra={
                "path": str(temporary_file),
            },
        )

    # =========================================================================
    # Domain Builders
    # =========================================================================

    def _build_document(
        self,
        *,
        knowledge_base,
        upload_file: UploadFile,
        metadata: DocumentMetadata,
    ) -> Document:
        """
        Build a Document entity.
        """

        document = Document(
            knowledge_base_id=knowledge_base.id,
            title=metadata.title,
            description=metadata.description,
            document_type=DocumentTypeResolver.resolve(self._get_filename(upload_file)),
            source=DocumentSource.MANUAL,
            status=DocumentStatus.PENDING,
        )

        return document

    def _build_document_version(
        self,
        *,
        document: Document,
        upload_file: UploadFile,
        stored_document,
        content_hash: str,
    ) -> DocumentVersion:
        """
        Build a DocumentVersion entity.
        """

        version_number = self._document_version_repository.get_next_version_number(
            document.id
        )

        filename = self._get_filename(upload_file)

        version = DocumentVersion(
            document_id=document.id,
            version_number=version_number,
            version_label=f"v{version_number}",
            file_name=filename,
            file_extension=Path(filename).suffix.lower(),
            mime_type=upload_file.content_type,
            file_size_bytes=stored_document.file_size_bytes,
            content_hash=content_hash,
            storage_provider=stored_document.provider,
            storage_path=stored_document.relative_path,
        )

        return version

    # =========================================================================
    # Persistence
    # =========================================================================

    def _persist_document(
        self,
        document: Document,
    ) -> Document:
        """
        Persist Document.
        """

        document = self._document_repository.create(document)

        logger.info(
            "Document created.",
            extra={
                "document_id": str(document.id),
            },
        )

        return document

    def _persist_document_version(
        self,
        version: DocumentVersion,
    ) -> DocumentVersion:
        """
        Persist DocumentVersion.
        """

        version = self._document_version_repository.create(version)

        logger.info(
            "Document version created.",
            extra={
                "document_version_id": str(version.id),
                "version_number": version.version_number,
            },
        )

        return version

    # =========================================================================
    # Processing
    # =========================================================================

    def _trigger_ingestion(
        self,
        *,
        document: Document,
        version: DocumentVersion,
        stored_document,
    ) -> None:
        """
        Trigger document ingestion.

        UploadService delegates the complete processing
        pipeline to DocumentIngestionService.
        """

        logger.info(
            "Starting document ingestion.",
            extra={
                "document_id": str(document.id),
                "version_id": str(version.id),
            },
        )

        metadata = self._build_ingestion_metadata(
            document=document,
            version=version,
        )

        self._ingestion_service.ingest(
            source=stored_document.absolute_path,
            document_id=document.id,
            document_version_id=version.id,
            knowledge_base_id=UUID(str(document.knowledge_base_id)),
            metadata=metadata,
        )

    # =========================================================================
    # Response
    # =========================================================================

    def _build_response(
        self,
        *,
        document: Document,
        version: DocumentVersion,
        stored_document,
        upload_file: UploadFile,
    ) -> DocumentUploadResponse:
        """
        Build upload response.
        """

        return DocumentUploadResponse(
            document_id=document.id,
            version_id=version.id,
            knowledge_base_id=UUID(str(document.knowledge_base_id)),
            filename=stored_document.file_name,
            original_filename=upload_file.filename,
            content_type=upload_file.content_type or "",
            size_bytes=stored_document.file_size_bytes,
            storage_path=stored_document.relative_path,
            status=document.status.value,
            uploaded_at=version.created_at,
        )

    # =========================================================================
    # Helpers
    # =========================================================================

    def _build_ingestion_metadata(
        self,
        *,
        document: Document,
        version: DocumentVersion,
    ) -> dict[str, str]:
        """
        Build metadata supplied to the ingestion pipeline.
        """

        return {
            "document_id": str(document.id),
            "document_version_id": str(version.id),
            "knowledge_base_id": str(document.knowledge_base_id),
        }
