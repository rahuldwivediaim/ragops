"""
Unit tests for Pinecone infrastructure provisioning.

The tests mock the Pinecone control-plane client. No real Pinecone resource is
created, modified, or deleted by this test module.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from backend.vector_store.provisioning.models import VectorIndexSpec
from backend.vector_store.provisioning.pinecone import (
    PineconeInfrastructureProvider,
)


def _description(
    *,
    dimension: int = 1536,
    metric: str = "cosine",
    ready: bool = True,
    cloud: str = "aws",
    region: str = "us-east-1",
) -> SimpleNamespace:
    return SimpleNamespace(
        dimension=dimension,
        metric=metric,
        status=SimpleNamespace(ready=ready),
        host="example.pinecone.io",
        spec=SimpleNamespace(cloud=cloud, region=region),
    )


@pytest.fixture
def client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def provider(client: MagicMock) -> PineconeInfrastructureProvider:
    with patch(
        "backend.vector_store.provisioning.pinecone.Pinecone",
        return_value=client,
    ):
        instance = PineconeInfrastructureProvider(
            api_key="test-key",
        )

    return instance


def test_existing_index_is_detected_without_mutation(
    provider: PineconeInfrastructureProvider,
    client: MagicMock,
) -> None:
    client.list_indexes.return_value = SimpleNamespace(
        names=lambda: ["customer-production"],
    )
    client.describe_index.return_value = _description()

    inspection = provider.inspect_index(
        index_name="customer-production",
    )

    assert inspection.exists is True
    assert inspection.index_name == "customer-production"
    assert inspection.dimension == 1536
    assert inspection.metric == "cosine"
    assert inspection.ready is True
    client.create_index.assert_not_called()


def test_missing_existing_customer_index_is_rejected(
    provider: PineconeInfrastructureProvider,
    client: MagicMock,
) -> None:
    client.list_indexes.return_value = SimpleNamespace(
        names=lambda: [],
    )

    result = provider.validate_existing_index(
        spec=VectorIndexSpec(
            index_name="customer-production",
            namespace="ragops-hr",
            dimensions=1536,
        ),
    )

    assert result.compatible is False
    assert "does not exist" in result.summary
    client.create_index.assert_not_called()


def test_dimension_mismatch_is_rejected(
    provider: PineconeInfrastructureProvider,
    client: MagicMock,
) -> None:
    client.list_indexes.return_value = SimpleNamespace(
        names=lambda: ["customer-production"],
    )
    client.describe_index.return_value = _description(
        dimension=768,
    )

    result = provider.validate_existing_index(
        spec=VectorIndexSpec(
            index_name="customer-production",
            namespace="ragops-hr",
            dimensions=1536,
        ),
    )

    assert result.compatible is False
    assert "dimension mismatch" in result.summary.lower()
    client.create_index.assert_not_called()


def test_metric_mismatch_is_rejected(
    provider: PineconeInfrastructureProvider,
    client: MagicMock,
) -> None:
    client.list_indexes.return_value = SimpleNamespace(
        names=lambda: ["customer-production"],
    )
    client.describe_index.return_value = _description(
        metric="dotproduct",
    )

    result = provider.validate_existing_index(
        spec=VectorIndexSpec(
            index_name="customer-production",
            namespace="ragops-hr",
            dimensions=1536,
            metric="cosine",
        ),
    )

    assert result.compatible is False
    assert "metric mismatch" in result.summary.lower()
    client.create_index.assert_not_called()


def test_compatible_existing_index_is_accepted(
    provider: PineconeInfrastructureProvider,
    client: MagicMock,
) -> None:
    client.list_indexes.return_value = SimpleNamespace(
        names=lambda: ["customer-production"],
    )
    client.describe_index.return_value = _description()

    result = provider.validate_existing_index(
        spec=VectorIndexSpec(
            index_name="customer-production",
            namespace="ragops-hr",
            dimensions=1536,
            metric="cosine",
        ),
    )

    assert result.compatible is True
    assert result.inspection is not None
    assert result.inspection.index_name == "customer-production"
    client.create_index.assert_not_called()


def test_managed_mode_creates_missing_index(
    provider: PineconeInfrastructureProvider,
    client: MagicMock,
) -> None:
    client.list_indexes.side_effect = [
        SimpleNamespace(names=lambda: []),
        SimpleNamespace(names=lambda: ["ragops-prod-acme"]),
    ]
    client.describe_index.return_value = _description()

    inspection = provider.ensure_index(
        spec=VectorIndexSpec(
            index_name="ragops-prod-acme",
            namespace="ragops-hr",
            dimensions=1536,
            metric="cosine",
            cloud="aws",
            region="us-east-1",
        ),
    )

    client.create_index.assert_called_once()
    call = client.create_index.call_args
    assert call.kwargs["name"] == "ragops-prod-acme"
    assert call.kwargs["dimension"] == 1536
    assert call.kwargs["metric"] == "cosine"
    assert call.kwargs["spec"].cloud == "aws"
    assert call.kwargs["spec"].region == "us-east-1"
    assert inspection.exists is True


def test_managed_mode_does_not_recreate_incompatible_existing_index(
    provider: PineconeInfrastructureProvider,
    client: MagicMock,
) -> None:
    client.list_indexes.return_value = SimpleNamespace(
        names=lambda: ["ragops-prod-acme"],
    )
    client.describe_index.return_value = _description(
        dimension=768,
    )

    with pytest.raises(ValueError, match="dimension mismatch"):
        provider.ensure_index(
            spec=VectorIndexSpec(
                index_name="ragops-prod-acme",
                namespace="ragops-hr",
                dimensions=1536,
            ),
        )

    client.create_index.assert_not_called()


def test_close_closes_client(
    provider: PineconeInfrastructureProvider,
    client: MagicMock,
) -> None:
    provider.close()
    client.close.assert_called_once()
