"""Tests for durable ingestion execution initialization."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from uuid import uuid4

# The local snapshot does not include the Pinecone SDK in its test environment.
# Stub only the provider module so the orchestration service can be imported.
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

openai_module = types.ModuleType("openai")


class OpenAI:  # pragma: no cover - import stub only
    pass


openai_module.OpenAI = OpenAI
sys.modules.setdefault("openai", openai_module)

from backend.document_processing.pipeline.result import ProcessingResult  # noqa: E402
from backend.services.document_ingestion_service import DocumentIngestionService  # noqa: E402


class FakeTracker:
    def __init__(self) -> None:
        self.events: list[str] = []

    def start(self, **kwargs):
        self.events.append("tracker.start")
        return object()

    def complete(self, context) -> None:
        self.events.append("tracker.complete")

    def fail(self, context, *, exception) -> None:
        self.events.append("tracker.fail")


class FakePipeline:
    def __init__(self, result: ProcessingResult) -> None:
        self.result = result
        self.events: list[str] = []

    def execute(self, context, observer=None):
        self.events.append("pipeline.execute")
        if self.result.success:
            context.chunks = [types.SimpleNamespace(text="chunk")]
            context.parsing_metadata = types.SimpleNamespace(id=uuid4())
        return self.result


class FakeProcessingJobService:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeParsingMetadataRepository:
    def get_by_document_version(self, document_version_id):
        return types.SimpleNamespace(id=uuid4())

    def create(self, entity):
        raise AssertionError("Existing parsing metadata should be reused in this test")


class FakePersistenceService:
    def __init__(self) -> None:
        self.events: list[str] = []
        self.ingestion = types.SimpleNamespace(
            id=uuid4(),
            total_chunks=0,
            total_embeddings=0,
            total_vectors_written=0,
        )

    def create_ingestion(self, **kwargs):
        self.events.append("create_ingestion")
        return self.ingestion

    def persist(self, **kwargs):
        self.events.append("persist")
        return self.ingestion

    def mark_failed(self, **kwargs):
        self.events.append("mark_failed")
        return self.ingestion


def test_ingestion_is_created_before_pipeline_execution(tmp_path: Path) -> None:
    source = tmp_path / "document.txt"
    source.write_text("content", encoding="utf-8")

    tracker = FakeTracker()
    pipeline = FakePipeline(
        ProcessingResult.completed(stage="Chunking", duration=0),
    )
    persistence = FakePersistenceService()
    processing_jobs = FakeProcessingJobService()

    service = DocumentIngestionService(
        tracker=tracker,
        pipeline=pipeline,
        parsing_metadata_repository=FakeParsingMetadataRepository(),
        persistence_service=persistence,
        processing_job_service=processing_jobs,
    )

    service.ingest(
        source=source,
        document_id=uuid4(),
        document_version_id=uuid4(),
        knowledge_base_id=uuid4(),
    )

    assert persistence.events == ["create_ingestion", "persist"]
    assert pipeline.events == ["pipeline.execute"]


def test_pipeline_failure_marks_the_durable_ingestion_failed(tmp_path: Path) -> None:
    source = tmp_path / "document.txt"
    source.write_text("content", encoding="utf-8")

    tracker = FakeTracker()
    pipeline = FakePipeline(
        ProcessingResult.failed_result(
            stage="Parsing",
            exception=ValueError("parse failed"),
            duration=0,
        ),
    )
    persistence = FakePersistenceService()
    processing_jobs = FakeProcessingJobService()

    service = DocumentIngestionService(
        tracker=tracker,
        pipeline=pipeline,
        parsing_metadata_repository=FakeParsingMetadataRepository(),
        persistence_service=persistence,
        processing_job_service=processing_jobs,
    )

    try:
        service.ingest(
            source=source,
            document_id=uuid4(),
            document_version_id=uuid4(),
            knowledge_base_id=uuid4(),
        )
    except ValueError as exc:
        assert str(exc) == "parse failed"
    else:
        raise AssertionError("Expected ingestion failure")

    assert persistence.events == ["create_ingestion", "mark_failed"]
    assert tracker.events == ["tracker.start", "tracker.fail"]


def test_create_ingestion_commits_before_processing_starts() -> None:
    from backend.models.enums import IngestionStatus
    from backend.services.ingestion_persistence_service import (
        IngestionPersistenceService,
    )

    class FakeSession:
        def __init__(self) -> None:
            self.added = None
            self.commit_count = 0
            self.refresh_count = 0

        def add(self, entity) -> None:
            self.added = entity

        def commit(self) -> None:
            self.commit_count += 1

        def refresh(self, entity) -> None:
            self.refresh_count += 1

    session = FakeSession()
    service = IngestionPersistenceService(
        session=session,
        embedding_provider=object(),
        vector_store=object(),
    )

    profile = types.SimpleNamespace(id=uuid4(), dimensions=1536)
    vector_index = types.SimpleNamespace(id=uuid4(), dimensions=1536)

    service._get_or_create_embedding_profile = lambda **kwargs: profile
    service._get_or_create_vector_index = lambda **kwargs: vector_index

    ingestion = service.create_ingestion(
        document_version_id=uuid4(),
        trigger_source="UPLOAD",
    )

    assert ingestion.status == IngestionStatus.RUNNING
    assert ingestion.total_chunks == 0
    assert ingestion.embedding_profile_id == profile.id
    assert ingestion.vector_index_id == vector_index.id
    assert session.added is ingestion
    assert session.commit_count == 1
    assert session.refresh_count == 1
