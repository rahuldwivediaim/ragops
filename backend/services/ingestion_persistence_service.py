"""
Persistence and external-index orchestration for document ingestion.

This service owns the persistence boundary between the in-memory document
processing pipeline and the persistent ingestion/chunk/embedding records.

The processing pipeline remains responsible for:
    validation -> parsing -> chunking

This service is responsible for:
    ingestion configuration -> DB chunks -> embeddings -> Pinecone -> DB
    embedding metadata -> ingestion statistics.

Chunk persistence is committed at the CHUNKING checkpoint before embedding
generation begins. This makes chunks a durable recovery artifact.
Embedding metadata and final ingestion statistics are committed only after
Pinecone indexing succeeds.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.common.config.loader import load_settings
from backend.embeddings.providers.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from backend.models.chunk import Chunk as DbChunk
from backend.models.embedding import Embedding
from backend.models.embedding_profile import EmbeddingProfile
from backend.models.enums import  IngestionStatus, StorageProvider
from backend.models.enums import VectorProvider
from backend.models.ingestion import Ingestion
from backend.models.vector_index import VectorIndex
from backend.models.enums import PipelineStage
from backend.services.processing_job_service import ProcessingJobService
from backend.vector_store.providers.pinecone_provider import PineconeProvider
from backend.services.embedding_profile_service import (
    EmbeddingProfileService,
)

class IngestionPersistenceService:
    """
    Persist and index the output of document processing.

    The service deliberately accepts already-created provider instances.
    Provider construction therefore remains outside the persistence layer and
    existing provider abstractions are reused unchanged.
    """

    def __init__(
        self,
        *,
        session: Session,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: PineconeProvider,
    ) -> None:
        self._session = session
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

        self._embedding_profile_service = EmbeddingProfileService(
            session=session,
            embedding_provider=embedding_provider,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_ingestion(
        self,
        *,
        document_version_id: UUID,
        trigger_source: str = "UPLOAD",
    ) -> Ingestion:
        """Create and durably initialize an ingestion execution.

        The execution record is committed before document processing starts.
        This gives every subsequent processing stage a durable ``ingestion_id``
        for processing jobs, pipeline events and recovery operations.

        Embedding and vector-index configuration are resolved before the
        ingestion is created because those foreign keys are mandatory.
        """

        settings = load_settings()

        embedding_profile = self._get_or_create_embedding_profile(
            settings=settings,
        )

        vector_index = self._get_or_create_vector_index(
            settings=settings,
            embedding_profile=embedding_profile,
        )

        self._validate_dimensions(
            embedding_profile=embedding_profile,
            vector_index=vector_index,
        )

        ingestion = Ingestion(
            document_version_id=document_version_id,
            embedding_profile_id=embedding_profile.id,
            vector_index_id=vector_index.id,
            status=IngestionStatus.RUNNING,
            trigger_source=trigger_source,
            total_chunks=0,
        )

        self._session.add(ingestion)
        self._session.commit()
        self._session.refresh(ingestion)

        return ingestion

    def mark_failed(
        self,
        *,
        ingestion: Ingestion,
        exception: Exception,
    ) -> Ingestion:
        """Persist a failed ingestion execution without deleting its history."""

        self._session.rollback()

        persisted_ingestion = self._session.get(
            Ingestion,
            ingestion.id,
        )

        if persisted_ingestion is None:
            raise RuntimeError(
                f"Ingestion '{ingestion.id}' no longer exists while recording "
                "the failure."
            )

        persisted_ingestion.status = IngestionStatus.FAILED
        persisted_ingestion.error_message = str(exception)

        self._session.commit()
        self._session.refresh(persisted_ingestion)

        return persisted_ingestion

    def persist(
        self,
        *,
        ingestion: Ingestion,
        document_id: UUID,
        document_version_id: UUID,
        knowledge_base_id: UUID,
        source_filename: str,
        chunks: list[Any],
        metadata: dict[str, Any] | None = None,
        processing_job_service: ProcessingJobService | None = None,
    ) -> Ingestion:
        """
        Persist chunks, generate embeddings and index them.

        Parameters
        ----------
        document_id:
            Source document identifier.

        document_version_id:
            Document version being ingested.

        knowledge_base_id:
            Knowledge Base owning the document.

        source_filename:
            Original/stored filename used in vector metadata.

        chunks:
            In-memory document-processing Chunk objects.

        metadata:
            Additional document metadata to forward to Pinecone.

        Returns
        -------
        Ingestion
            Completed ingestion record.

        Raises
        ------
        ValueError
            If configuration or processing output is invalid.

        Exception
            Any embedding or Pinecone failure is propagated after rolling
            back the PostgreSQL transaction.
        """

        if not chunks:
            raise ValueError("Document processing produced no chunks.")

        if ingestion.status != IngestionStatus.RUNNING:
            raise ValueError(
                "Ingestion must be in RUNNING state before persistence "
                f"continues; current status={ingestion.status.value!r}."
            )

        ingestion.total_chunks = len(chunks)

        try:
            try:
                db_chunks = self._persist_chunks(
                    ingestion=ingestion,
                    chunks=chunks,
                )

                # CHUNKING is a durable recovery checkpoint. The chunk records
                # must be committed before downstream embedding/indexing work
                # begins. If a later stage fails, the chunks remain available
                # for recovery and retry.
                ingestion.total_chunks = len(db_chunks)
                self._session.commit()
                self._session.refresh(ingestion)
            except Exception as exc:
                if processing_job_service is not None:
                    processing_job_service.fail_stage(
                        ingestion_id=ingestion.id,
                        stage=PipelineStage.CHUNKING,
                        exception=exc,
                    )
                raise

            if processing_job_service is not None:
                processing_job_service.complete_stage(
                    ingestion_id=ingestion.id,
                    stage=PipelineStage.CHUNKING,
                    records_processed=len(db_chunks),
                )

            if processing_job_service is not None:
                processing_job_service.start_stage(
                    ingestion_id=ingestion.id,
                    stage=PipelineStage.EMBEDDING,
                )

            try:
                embedding_results = self._embedding_provider.embed_batch(
                    [chunk.text for chunk in chunks],
                )

                if len(embedding_results) != len(chunks):
                    raise RuntimeError(
                        "Embedding provider returned a different number of "
                        "embeddings than the number of chunks."
                    )

                embedding_profile = self._session.get(
                    EmbeddingProfile,
                    ingestion.embedding_profile_id,
                )
                if embedding_profile is None:
                    raise RuntimeError(
                        f"Embedding profile '{ingestion.embedding_profile_id}' "
                        "could not be loaded for ingestion."
                    )

                vectors: list[dict[str, Any]] = []
                embedding_records: list[Embedding] = []

                for processing_chunk, db_chunk, embedding_result in zip(
                    chunks, db_chunks, embedding_results, strict=True
                ):
                    if embedding_result.dimensions != embedding_profile.dimensions:
                        raise ValueError(
                            "Embedding dimensions do not match the configured "
                            f"profile: expected {embedding_profile.dimensions}, "
                            f"received {embedding_result.dimensions}."
                        )

                    vector_identifier = self._build_vector_identifier(
                        document_id=document_id,
                        document_version_id=document_version_id,
                        chunk_id=db_chunk.id,
                    )

                    vector_metadata = self._build_vector_metadata(
                        document_id=document_id,
                        document_version_id=document_version_id,
                        knowledge_base_id=knowledge_base_id,
                        source_filename=source_filename,
                        processing_chunk=processing_chunk,
                        db_chunk=db_chunk,
                        embedding_result=embedding_result,
                        extra_metadata=metadata,
                    )

                    vectors.append({
                        "id": vector_identifier,
                        "values": embedding_result.vector,
                        "metadata": vector_metadata,
                    })

                    embedding_records.append(
                        Embedding(
                            ingestion_id=ingestion.id,
                            chunk_id=db_chunk.id,
                            vector_index_id=ingestion.vector_index_id,
                            vector_identifier=vector_identifier,
                            dimensions=embedding_result.dimensions,
                            provider=embedding_result.provider,
                            model_name=embedding_result.model_name,
                            embedding_version=embedding_result.embedding_version,
                        )
                    )

                if processing_job_service is not None:
                    processing_job_service.complete_stage(
                        ingestion_id=ingestion.id,
                        stage=PipelineStage.EMBEDDING,
                        records_processed=len(embedding_results),
                    )
            except Exception as exc:
                if processing_job_service is not None:
                    processing_job_service.fail_stage(
                        ingestion_id=ingestion.id,
                        stage=PipelineStage.EMBEDDING,
                        exception=exc,
                    )
                raise

            if processing_job_service is not None:
                processing_job_service.start_stage(
                    ingestion_id=ingestion.id,
                    stage=PipelineStage.INDEXING,
                )

            try:
                self._vector_store.upsert_batch(vectors)
            except Exception as exc:
                if processing_job_service is not None:
                    processing_job_service.fail_stage(
                        ingestion_id=ingestion.id,
                        stage=PipelineStage.INDEXING,
                        exception=exc,
                    )
                raise

            if processing_job_service is not None:
                processing_job_service.complete_stage(
                    ingestion_id=ingestion.id,
                    stage=PipelineStage.INDEXING,
                    records_processed=len(vectors),
                )

            self._session.add_all(embedding_records)

            ingestion.successful_chunks = len(db_chunks)
            ingestion.failed_chunks = 0
            ingestion.total_embeddings = len(embedding_records)
            ingestion.total_vectors_written = len(vectors)
            ingestion.status = IngestionStatus.COMPLETED
            ingestion.error_message = None

            self._session.commit()
            self._session.refresh(ingestion)

            return ingestion

        except Exception as exc:
            self._session.rollback()
            self.mark_failed(
                ingestion=ingestion,
                exception=exc,
            )
            raise

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _get_or_create_embedding_profile(
        self,
        *,
        settings: Any,
    ) -> EmbeddingProfile:
        """
        Resolve the persistent embedding profile from application settings.

        The configured provider value is normalized to the canonical
        EmbeddingProvider enum representation before persistence.

        The profile name is deterministic so repeated ingestion runs reuse
        the same configuration record
        """
        return self._embedding_profile_service.get_or_create(
                settings=settings,
        )

    def _get_or_create_vector_index(
        self,
        *,
        settings: Any,
        embedding_profile: EmbeddingProfile,
    ) -> VectorIndex:
        """
         Resolve the persistent vector-index configuration.

        The configured vector-store provider value is normalized to the
        canonical VectorProvider enum representation before persistence.

        The index name and namespace are taken from application settings.
        """

        provider = VectorProvider(
            settings.vector_store.provider.value.upper(),
        )

        index_name = settings.vector_store.index_name
        namespace = settings.vector_store.namespace

        statement = select(VectorIndex).where(
            VectorIndex.provider == provider,
            VectorIndex.index_name == index_name,
        )

        vector_index = self._session.scalar(statement)

        if vector_index is not None:
            if not vector_index.is_active:
                raise ValueError(
                    f"Vector index '{index_name}' is inactive."
                )

            if vector_index.dimensions != embedding_profile.dimensions:
                raise ValueError(
                    "Vector index dimensions do not match the embedding "
                    f"profile: index={vector_index.dimensions}, "
                    f"profile={embedding_profile.dimensions}."
                )

            if vector_index.embedding_profile_id != embedding_profile.id:
                raise ValueError(
                    "Configured vector index is associated with a different "
                    "embedding profile."
                )

            if vector_index.namespace != namespace:
                raise ValueError(
                    "Configured vector index namespace does not match "
                    f"application configuration: "
                    f"database={vector_index.namespace!r}, "
                    f"configuration={namespace!r}."
                )

            return vector_index

        vector_index = VectorIndex(
            embedding_profile_id=embedding_profile.id,
            name=f"{provider.value}-{index_name}",
            description=(
                "Application-configured vector index for "
                f"{provider.value}."
            ),
            provider=provider,
            index_name=index_name,
            namespace=namespace,
            dimensions=embedding_profile.dimensions,
            storage_provider=StorageProvider.LOCAL,
            is_default=True,
            is_active=True,
        )

        self._session.add(vector_index)
        self._session.flush()

        return vector_index

    # ------------------------------------------------------------------
    # Chunk persistence
    # ------------------------------------------------------------------

    def _persist_chunks(
        self,
        *,
        ingestion: Ingestion,
        chunks: list[Any],
    ) -> list[DbChunk]:
        """
        Convert transient processing chunks into persistent DB chunks.
        """

        existing_chunks = list(
            self._session.scalars(
                select(DbChunk)
                .where(DbChunk.ingestion_id == ingestion.id)
                .order_by(DbChunk.chunk_number),
            ).all()
        )

        if existing_chunks:
            if not self._chunks_match(
                existing_chunks=existing_chunks,
                processing_chunks=chunks,
            ):
                raise ValueError(
                    "Durable chunks already exist for this ingestion, but "
                    "they do not match the current processing output. "
                    "Refusing to create duplicate or inconsistent chunks."
                )

            return existing_chunks

        db_chunks: list[DbChunk] = []

        for processing_chunk in chunks:
            if not processing_chunk.text or not processing_chunk.text.strip():
                raise ValueError(
                    f"Chunk {processing_chunk.chunk_number} contains no text."
                )

            db_chunk = DbChunk(
                ingestion_id=ingestion.id,
                chunk_number=processing_chunk.chunk_number,
                character_start=processing_chunk.character_start,
                character_end=processing_chunk.character_end,
                token_count=processing_chunk.token_count,
                text=processing_chunk.text,
            )

            db_chunks.append(db_chunk)

        self._session.add_all(db_chunks)
        self._session.flush()

        return db_chunks

    @staticmethod
    def _chunks_match(
        *,
        existing_chunks: list[DbChunk],
        processing_chunks: list[Any],
    ) -> bool:
        """Verify that durable chunks can safely be reused for recovery."""

        if len(existing_chunks) != len(processing_chunks):
            return False

        for existing, processing in zip(
            existing_chunks,
            processing_chunks,
            strict=True,
        ):
            if existing.chunk_number != processing.chunk_number:
                return False
            if existing.text != processing.text:
                return False
            if existing.character_start != processing.character_start:
                return False
            if existing.character_end != processing.character_end:
                return False
            if existing.token_count != processing.token_count:
                return False

        return True

    # ------------------------------------------------------------------
    # Vector construction
    # ------------------------------------------------------------------

    @staticmethod
    def _build_vector_identifier(
        *,
        document_id: UUID,
        document_version_id: UUID,
        chunk_id: UUID,
    ) -> str:
        """
        Build a stable vector identifier.

        The UUID of the persistent chunk is part of the identifier, so the
        identifier remains stable for the lifetime of that chunk.
        """

        return (
            f"doc-{document_id}-"
            f"version-{document_version_id}-"
            f"chunk-{chunk_id}"
        )

    @staticmethod
    def _build_vector_metadata(
        *,
        document_id: UUID,
        document_version_id: UUID,
        knowledge_base_id: UUID,
        source_filename: str,
        processing_chunk: Any,
        db_chunk: DbChunk,
        embedding_result: Any,
        extra_metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Build the complete metadata contract used by retrieval.
        """

        metadata: dict[str, Any] = {
            "document_id": str(document_id),
            "document_version_id": str(document_version_id),
            "knowledge_base_id": str(knowledge_base_id),
            "chunk_id": str(db_chunk.id),
            "chunk_number": db_chunk.chunk_number,
            "filename": source_filename,
            "provider": embedding_result.provider,
            "model_name": embedding_result.model_name,
            "embedding_version": str(
                embedding_result.embedding_version,
            ),
            "text": db_chunk.text,
            "character_start": db_chunk.character_start,
            "character_end": db_chunk.character_end,
        }

        page_number = getattr(
            processing_chunk,
            "page_number",
            None,
        )

        if page_number is not None:
            metadata["page_number"] = page_number

        if db_chunk.token_count is not None:
            metadata["token_count"] = db_chunk.token_count

        if extra_metadata:
            for key, value in extra_metadata.items():
                if key not in metadata:
                    metadata[key] = value

        return metadata

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    

    @staticmethod
    def _validate_dimensions(
        *,
        embedding_profile: EmbeddingProfile,
        vector_index: VectorIndex,
    ) -> None:
        """
        Validate the embedding/vector dimension contract.
        """

        if embedding_profile.dimensions != vector_index.dimensions:
            raise ValueError(
                "Embedding profile and vector index dimensions must match."
            )


__all__ = [
    "IngestionPersistenceService",
]