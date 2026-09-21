from __future__ import annotations

from unittest.mock import Mock
from uuid import uuid4

import sys
import types

# The isolated snapshot test environment does not include provider SDKs.
# Stub only their import surfaces; no external provider call is made.
openai_module = types.ModuleType("openai")


class OpenAI:  # pragma: no cover - import stub only
    pass


openai_module.OpenAI = OpenAI
sys.modules.setdefault("openai", openai_module)

pinecone_module = types.ModuleType(
    "backend.vector_store.providers.pinecone_provider",
)


class PineconeProvider:  # pragma: no cover - import stub only
    pass


pinecone_module.PineconeProvider = PineconeProvider
sys.modules.setdefault(
    "backend.vector_store.providers.pinecone_provider",
    pinecone_module,
)

from backend.embeddings.models.embedding_result import EmbeddingResult  # noqa: E402
from backend.models.enums import IngestionStatus, PipelineStage  # noqa: E402
from backend.models.ingestion import Ingestion  # noqa: E402
from backend.models.embedding_profile import EmbeddingProfile  # noqa: E402
from backend.services.ingestion_persistence_service import IngestionPersistenceService  # noqa: E402


class FakeScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return list(self._values)


class FakeSession:
    def __init__(self, *, existing_chunks=None, fail_first_commit=False):
        self.existing_chunks = list(existing_chunks or [])
        self.fail_first_commit = fail_first_commit
        self.commit_count = 0
        self.events: list[str] = []
        self.added: list[object] = []
        self.embedding_profile = EmbeddingProfile(
            name="OPENAI-text-embedding-3-small-1536",
            provider="OPENAI",
            model_name="text-embedding-3-small",
            dimensions=1536,
            is_default=True,
            is_active=True,
        )

    def scalars(self, statement):
        self.events.append("scalars")
        return FakeScalarResult(self.existing_chunks)

    def add_all(self, entities):
        self.events.append("add_all")
        self.added.extend(entities)

    def flush(self):
        self.events.append("flush")
        for entity in self.added:
            if getattr(entity, "id", None) is None:
                entity.id = uuid4()

    def commit(self):
        self.events.append("commit")
        self.commit_count += 1
        if self.fail_first_commit and self.commit_count == 1:
            raise RuntimeError("checkpoint commit failed")

    def refresh(self, entity):
        self.events.append("refresh")

    def rollback(self):
        self.events.append("rollback")

    def get(self, model, identifier):
        if model is EmbeddingProfile:
            return self.embedding_profile
        if model is Ingestion:
            return self.ingestion
        return None


class FakeEmbeddingProvider:
    dimensions = 1536

    def embed_batch(self, texts):
        return [
            EmbeddingResult(
                vector=[0.1] * 1536,
                provider="OPENAI",
                model_name="text-embedding-3-small",
                dimensions=1536,
            )
            for _ in texts
        ]


class FakeVectorStore:
    def __init__(self, *, failure: Exception | None = None):
        self.failure = failure
        self.upsert_calls = 0

    def upsert_batch(self, vectors):
        self.upsert_calls += 1
        if self.failure is not None:
            raise self.failure


class FakeProcessingJobService:
    def __init__(self):
        self.events: list[tuple[str, PipelineStage]] = []

    def start_stage(self, *, ingestion_id, stage):
        self.events.append(("start", stage))

    def complete_stage(self, *, ingestion_id, stage, records_processed=0):
        self.events.append(("complete", stage))

    def fail_stage(self, *, ingestion_id, stage, exception):
        self.events.append(("fail", stage))


def _build_ingestion() -> Ingestion:
    return Ingestion(
        id=uuid4(),
        document_version_id=uuid4(),
        embedding_profile_id=uuid4(),
        vector_index_id=uuid4(),
        status=IngestionStatus.RUNNING,
        trigger_source="UPLOAD",
    )


def _build_chunks():
    return [
        type(
            "ProcessingChunk",
            (),
            {
                "chunk_number": 1,
                "character_start": 0,
                "character_end": 5,
                "token_count": 2,
                "text": "hello",
            },
        )()
    ]


def test_chunk_checkpoint_is_committed_before_embedding_starts() -> None:
    session = FakeSession()
    ingestion = _build_ingestion()
    session.ingestion = ingestion
    jobs = FakeProcessingJobService()
    vector_store = FakeVectorStore()

    service = IngestionPersistenceService(
        session=session,
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=vector_store,
    )

    result = service.persist(
        ingestion=ingestion,
        document_id=uuid4(),
        document_version_id=ingestion.document_version_id,
        knowledge_base_id=uuid4(),
        source_filename="employee.txt",
        chunks=_build_chunks(),
        processing_job_service=jobs,
    )

    assert result.status == IngestionStatus.COMPLETED
    assert jobs.events[:4] == [
        ("complete", PipelineStage.CHUNKING),
        ("start", PipelineStage.EMBEDDING),
        ("complete", PipelineStage.EMBEDDING),
        ("start", PipelineStage.INDEXING),
    ]
    assert session.events.index("commit") < session.events.index("refresh")
    assert vector_store.upsert_calls == 1


def test_indexing_failure_preserves_durable_chunk_checkpoint() -> None:
    session = FakeSession()
    ingestion = _build_ingestion()
    session.ingestion = ingestion
    jobs = FakeProcessingJobService()
    vector_store = FakeVectorStore(failure=RuntimeError("pinecone unavailable"))

    service = IngestionPersistenceService(
        session=session,
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=vector_store,
    )

    try:
        service.persist(
            ingestion=ingestion,
            document_id=uuid4(),
            document_version_id=ingestion.document_version_id,
            knowledge_base_id=uuid4(),
            source_filename="employee.txt",
            chunks=_build_chunks(),
            processing_job_service=jobs,
        )
    except RuntimeError as exc:
        assert str(exc) == "pinecone unavailable"
    else:
        raise AssertionError("Expected indexing failure")

    assert "commit" in session.events
    assert jobs.events == [
        ("complete", PipelineStage.CHUNKING),
        ("start", PipelineStage.EMBEDDING),
        ("complete", PipelineStage.EMBEDDING),
        ("start", PipelineStage.INDEXING),
        ("fail", PipelineStage.INDEXING),
    ]
    assert ingestion.status == IngestionStatus.FAILED


def test_existing_matching_chunks_are_reused_instead_of_duplicated() -> None:
    ingestion = _build_ingestion()
    processing_chunks = _build_chunks()

    from backend.models.chunk import Chunk

    existing = Chunk(
        id=uuid4(),
        ingestion_id=ingestion.id,
        chunk_number=1,
        character_start=0,
        character_end=5,
        token_count=2,
        text="hello",
    )

    session = FakeSession(existing_chunks=[existing])
    session.ingestion = ingestion

    service = IngestionPersistenceService(
        session=session,
        embedding_provider=Mock(),
        vector_store=Mock(),
    )

    result = service._persist_chunks(
        ingestion=ingestion,
        chunks=processing_chunks,
    )

    assert result == [existing]
    assert session.added == []
