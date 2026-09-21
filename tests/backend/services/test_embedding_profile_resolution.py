
from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from uuid import uuid4

import pytest

# Stub external provider imports used during service import.
openai_module = types.ModuleType("openai")


class OpenAI:  # pragma: no cover
    pass


openai_module.OpenAI = OpenAI
sys.modules.setdefault("openai", openai_module)

pinecone_module = types.ModuleType(
    "backend.vector_store.providers.pinecone_provider",
)


class PineconeProvider:  # pragma: no cover
    pass


pinecone_module.PineconeProvider = PineconeProvider
sys.modules.setdefault(
    "backend.vector_store.providers.pinecone_provider",
    pinecone_module,
)

from backend.models.embedding_profile import EmbeddingProfile  # noqa: E402
from backend.services.ingestion_persistence_service import (  # noqa: E402
    IngestionPersistenceService,
)


class FakeSession:
    def __init__(self, profile=None):
        self.profile = profile
        self.added = []
        self.flush_count = 0

    def scalar(self, statement):
        return self.profile

    def add(self, entity):
        self.added.append(entity)

    def flush(self):
        self.flush_count += 1
        for entity in self.added:
            if getattr(entity, "id", None) is None:
                entity.id = uuid4()


class FakeEmbeddingProvider:
    dimensions = 1536


def _settings(*, dimensions=1536):
    return SimpleNamespace(
        embeddings=SimpleNamespace(
            provider=SimpleNamespace(value="openai"),
            model="text-embedding-3-small",
            dimensions=dimensions,
        )
    )


def _service(session):
    return IngestionPersistenceService(
        session=session,
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=object(),
    )


def test_creates_embedding_profile_when_no_matching_profile_exists():
    session = FakeSession()
    service = _service(session)

    profile = service._get_or_create_embedding_profile(
        settings=_settings(),
    )

    assert profile.name == "OPENAI-text-embedding-3-small-1536"
    assert profile.model_name == "text-embedding-3-small"
    assert profile.dimensions == 1536
    assert profile.is_active is True
    assert session.added == [profile]
    assert session.flush_count == 1

    print(f"Created embedding profile: {profile.name}")


def test_reuses_existing_active_embedding_profile():
    existing_profile = EmbeddingProfile(
        id=uuid4(),
        name="OPENAI-text-embedding-3-small-1536",
        provider="OPENAI",
        model_name="text-embedding-3-small",
        dimensions=1536,
        is_default=True,
        is_active=True,
    )

    session = FakeSession(profile=existing_profile)
    service = _service(session)

    result = service._get_or_create_embedding_profile(
        settings=_settings(),
    )

    assert result is existing_profile
    assert session.added == []
    assert session.flush_count == 0

    print(f"Reused embedding profile: {result.name}")


def test_rejects_embedding_dimension_mismatch():
    session = FakeSession()
    service = _service(session)

    with pytest.raises(ValueError, match="Configured embedding dimensions"):
        service._get_or_create_embedding_profile(
            settings=_settings(dimensions=768),
        )

    print("Correctly rejected incompatible embedding dimensions")


def test_rejects_inactive_embedding_profile():
    inactive_profile = EmbeddingProfile(
        id=uuid4(),
        name="OPENAI-text-embedding-3-small-1536",
        provider="OPENAI",
        model_name="text-embedding-3-small",
        dimensions=1536,
        is_default=True,
        is_active=False,
    )

    session = FakeSession(profile=inactive_profile)
    service = _service(session)

    with pytest.raises(ValueError, match="is inactive"):
        service._get_or_create_embedding_profile(
            settings=_settings(),
        )

    print("Correctly rejected inactive embedding profile")