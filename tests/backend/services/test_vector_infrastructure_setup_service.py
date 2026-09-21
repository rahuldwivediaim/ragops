"""
Tests for VectorInfrastructureSetupService.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from backend.models.enums import (
    StorageProvider,
    VectorInfrastructureMode,
)
from backend.models.vector_index import VectorIndex
from backend.services.vector_infrastructure_setup_service import (
    VectorInfrastructureSetupService,
)
from backend.vector_store.provisioning.models import (
    VectorCompatibilityResult,
    VectorIndexInspection,
    VectorIndexSpec,
)


def _spec(
    *,
    index_name: str = "customer-production",
    namespace: str = "ragops-hr",
) -> VectorIndexSpec:
    """Build a standard test specification."""

    return VectorIndexSpec(
        index_name=index_name,
        namespace=namespace,
        dimensions=1536,
        metric="cosine",
        cloud="aws",
        region="us-east-1",
    )


def _inspection(
    *,
    index_name: str = "customer-production",
) -> VectorIndexInspection:
    """Build a ready physical-index inspection."""

    return VectorIndexInspection(
        exists=True,
        index_name=index_name,
        dimension=1536,
        metric="cosine",
        ready=True,
        host="https://example.pinecone.io",
        cloud="aws",
        region="us-east-1",
    )


def _session_mock(
    *,
    existing: VectorIndex | None = None,
) -> Mock:
    """Build a minimal SQLAlchemy-session mock."""

    session = Mock()

    result = Mock()
    result.scalar_one_or_none.return_value = existing

    session.execute.return_value = result

    return session


def test_ragops_managed_uses_ensure_index_and_persists_record() -> None:
    """RAGOps-managed setup creates/ensures infrastructure and persists it."""

    session = _session_mock()

    provider = Mock()
    provider.provider_name = "PINECONE"
    provider.ensure_index.return_value = _inspection()

    service = VectorInfrastructureSetupService(
        session=session,
        infrastructure_provider=provider,
    )

    embedding_profile_id = uuid4()

    result = service.setup(
        name="HR Knowledge Index",
        embedding_profile_id=embedding_profile_id,
        spec=_spec(),
        management_mode=VectorInfrastructureMode.RAGOPS_MANAGED,
        storage_provider=StorageProvider.LOCAL,
    )

    provider.ensure_index.assert_called_once()
    provider.validate_existing_index.assert_not_called()

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    persisted = session.add.call_args.args[0]

    assert isinstance(persisted, VectorIndex)
    assert persisted.name == "HR Knowledge Index"
    assert persisted.provider.value == "PINECONE"
    assert persisted.index_name == "customer-production"
    assert persisted.namespace == "ragops-hr"
    assert persisted.dimensions == 1536
    assert persisted.embedding_profile_id == embedding_profile_id
    assert persisted.management_mode == VectorInfrastructureMode.RAGOPS_MANAGED

    assert result is persisted


def test_customer_managed_validates_without_calling_ensure() -> None:
    """Customer-managed setup validates an existing index without creating it."""

    session = _session_mock()

    provider = Mock()
    provider.provider_name = "PINECONE"
    provider.validate_existing_index.return_value = VectorCompatibilityResult(
        compatible=True,
        inspection=_inspection(),
    )

    service = VectorInfrastructureSetupService(
        session=session,
        infrastructure_provider=provider,
    )

    result = service.setup(
        name="HR Customer Index",
        embedding_profile_id=uuid4(),
        spec=_spec(),
        management_mode=VectorInfrastructureMode.CUSTOMER_MANAGED,
    )

    provider.validate_existing_index.assert_called_once()
    provider.ensure_index.assert_not_called()

    persisted = session.add.call_args.args[0]

    assert isinstance(persisted, VectorIndex)
    assert persisted.management_mode == VectorInfrastructureMode.CUSTOMER_MANAGED

    assert result is persisted


def test_customer_managed_rejects_incompatible_index() -> None:
    """An incompatible customer index must never be persisted."""

    session = _session_mock()

    provider = Mock()
    provider.provider_name = "PINECONE"
    provider.validate_existing_index.return_value = VectorCompatibilityResult(
        compatible=False,
        messages=("Dimension mismatch.",),
        inspection=_inspection(),
    )

    service = VectorInfrastructureSetupService(
        session=session,
        infrastructure_provider=provider,
    )

    with pytest.raises(ValueError, match="Dimension mismatch"):
        service.setup(
            name="HR Customer Index",
            embedding_profile_id=uuid4(),
            spec=_spec(),
            management_mode=VectorInfrastructureMode.CUSTOMER_MANAGED,
        )

    provider.ensure_index.assert_not_called()
    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_customer_managed_rejects_missing_index() -> None:
    """A customer-managed index must already exist."""

    session = _session_mock()

    provider = Mock()
    provider.provider_name = "PINECONE"
    provider.validate_existing_index.return_value = VectorCompatibilityResult(
        compatible=False,
        messages=("Index does not exist.",),
        inspection=VectorIndexInspection(
            exists=False,
            index_name="customer-production",
        ),
    )

    service = VectorInfrastructureSetupService(
        session=session,
        infrastructure_provider=provider,
    )

    with pytest.raises(ValueError, match="Index does not exist"):
        service.setup(
            name="HR Customer Index",
            embedding_profile_id=uuid4(),
            spec=_spec(),
            management_mode=VectorInfrastructureMode.CUSTOMER_MANAGED,
        )

    provider.ensure_index.assert_not_called()
    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_existing_vector_index_is_reused_without_duplicate_persistence() -> None:
    """Repeated setup for the same compatible application record is idempotent."""

    embedding_profile_id = uuid4()

    existing = SimpleNamespace(
        provider="PINECONE",
        index_name="customer-production",
        namespace="ragops-hr",
        dimensions=1536,
        embedding_profile_id=embedding_profile_id,
        management_mode=VectorInfrastructureMode.CUSTOMER_MANAGED,
        is_active=True,
        deleted_at=None,
    )

    session = _session_mock(existing=existing)

    provider = Mock()
    provider.provider_name = "PINECONE"

    service = VectorInfrastructureSetupService(
        session=session,
        infrastructure_provider=provider,
    )

    result = service.setup(
        name="HR Customer Index",
        embedding_profile_id=embedding_profile_id,
        spec=_spec(),
        management_mode=VectorInfrastructureMode.CUSTOMER_MANAGED,
    )

    provider.ensure_index.assert_not_called()
    provider.validate_existing_index.assert_not_called()

    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.refresh.assert_not_called()

    assert result is existing


def test_existing_vector_index_with_different_mode_is_rejected() -> None:
    """An existing application record cannot silently change ownership mode."""

    embedding_profile_id = uuid4()

    existing = SimpleNamespace(
        provider="PINECONE",
        index_name="customer-production",
        namespace="ragops-hr",
        dimensions=1536,
        embedding_profile_id=embedding_profile_id,
        management_mode=VectorInfrastructureMode.RAGOPS_MANAGED,
        is_active=True,
        deleted_at=None,
    )

    session = _session_mock(existing=existing)

    provider = Mock()
    provider.provider_name = "PINECONE"

    service = VectorInfrastructureSetupService(
        session=session,
        infrastructure_provider=provider,
    )

    with pytest.raises(ValueError, match="management mode"):
        service.setup(
            name="HR Customer Index",
            embedding_profile_id=embedding_profile_id,
            spec=_spec(),
            management_mode=VectorInfrastructureMode.CUSTOMER_MANAGED,
        )

    provider.ensure_index.assert_not_called()
    provider.validate_existing_index.assert_not_called()

    session.add.assert_not_called()
    session.commit.assert_not_called()