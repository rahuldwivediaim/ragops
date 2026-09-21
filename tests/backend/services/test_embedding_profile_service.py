
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from backend.models.embedding_profile import EmbeddingProfile
from backend.services.embedding_profile_service import (
    EmbeddingProfileService,
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


def _settings(dimensions=1536):
    return SimpleNamespace(
        embeddings=SimpleNamespace(
            provider=SimpleNamespace(value="openai"),
            model="text-embedding-3-small",
            dimensions=dimensions,
        )
    )


def _service(session):
    return EmbeddingProfileService(
        session=session,
        embedding_provider=FakeEmbeddingProvider(),
    )


def test_creates_profile_when_missing():
    session = FakeSession()
    service = _service(session)

    profile = service.get_or_create(settings=_settings())

    assert profile.name == "OPENAI-text-embedding-3-small-1536"
    assert profile.model_name == "text-embedding-3-small"
    assert profile.dimensions == 1536
    assert profile.is_active is True
    assert session.added == [profile]
    assert session.flush_count == 1

    print(f"Created profile: {profile.name}")


def test_reuses_existing_active_profile():
    existing = EmbeddingProfile(
        id=uuid4(),
        name="OPENAI-text-embedding-3-small-1536",
        provider="OPENAI",
        model_name="text-embedding-3-small",
        dimensions=1536,
        is_default=True,
        is_active=True,
    )

    session = FakeSession(profile=existing)
    service = _service(session)

    result = service.get_or_create(settings=_settings())

    assert result is existing
    assert session.added == []
    assert session.flush_count == 0

    print(f"Reused profile: {result.name}")


def test_rejects_incompatible_dimensions():
    session = FakeSession()
    service = _service(session)

    with pytest.raises(
        ValueError,
        match="Configured embedding dimensions",
    ):
        service.get_or_create(settings=_settings(dimensions=768))

    print("Rejected incompatible dimensions")


def test_rejects_inactive_profile():
    inactive = EmbeddingProfile(
        id=uuid4(),
        name="OPENAI-text-embedding-3-small-1536",
        provider="OPENAI",
        model_name="text-embedding-3-small",
        dimensions=1536,
        is_default=True,
        is_active=False,
    )

    session = FakeSession(profile=inactive)
    service = _service(session)

    with pytest.raises(ValueError, match="is inactive"):
        service.get_or_create(settings=_settings())

    print("Rejected inactive profile")