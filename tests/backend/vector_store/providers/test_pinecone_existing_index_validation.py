"""
Real Pinecone customer-managed index validation test.

This test treats the existing `ragops-test-lifecycle` index as an
externally existing index and validates it without creating, modifying,
writing to, or deleting the index.

The index must have been created by the previous managed-provisioning test.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from backend.vector_store.provisioning.models import VectorIndexSpec
from backend.vector_store.provisioning.pinecone import (
    PineconeInfrastructureProvider,
)


def test_pinecone_existing_index_validation() -> None:
    """Validate an existing Pinecone index without provisioning it."""
    load_dotenv()

    api_key = os.getenv("PINECONE_API_KEY")
    assert api_key, "PINECONE_API_KEY is not configured in .env."

    dimensions_value = os.getenv("OPENAI_EMBEDDING_DIMENSIONS")
    dimensions = int(dimensions_value) if dimensions_value else 1536

    cloud = os.getenv("PINECONE_CLOUD", "aws")
    region = os.getenv("PINECONE_REGION", "us-east-1")

    index_name = "ragops-test-lifecycle"
    namespace = "ragops-hr"

    spec = VectorIndexSpec(
        index_name=index_name,
        namespace=namespace,
        dimensions=dimensions,
        metric="cosine",
        cloud=cloud,
        region=region,
    )

    infrastructure = PineconeInfrastructureProvider(
        api_key=api_key,
    )

    try:
        result = infrastructure.validate_existing_index(
            spec=spec,
        )

        assert result.compatible is True
        assert result.inspection is not None

        inspection = result.inspection

        assert inspection.exists is True
        assert inspection.index_name == index_name
        assert inspection.dimension == dimensions
        assert inspection.metric == "cosine"
        assert inspection.ready is True

        print("\n" + "=" * 80)
        print("RAGOps Customer-Managed Pinecone Validation Test")
        print("=" * 80)
        print(f"Existing Index : {index_name}")
        print(f"RAGOps Namespace: {namespace}")
        print(f"Dimension       : {inspection.dimension}")
        print(f"Metric          : {inspection.metric}")
        print(f"Ready           : {inspection.ready}")
        print()
        print("Status          : EXISTING INDEX IS COMPATIBLE")
        print()
        print("No index was created, modified, or deleted.")
        print("=" * 80)

    finally:
        infrastructure.close()