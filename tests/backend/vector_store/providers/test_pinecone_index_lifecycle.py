"""
Pinecone managed infrastructure provisioning integration test.

This test verifies that RAGOps can create a managed Pinecone index
when the index does not already exist.

IMPORTANT:
- This test intentionally does NOT delete the index.
- The resulting index can be inspected manually in the Pinecone console.
- Do not run this test repeatedly until the existing test index has been
  deleted or the test has been intentionally changed to reuse it.
- This test never touches the application's configured index.
"""

from __future__ import annotations

import os
import time

from dotenv import load_dotenv

from backend.vector_store.provisioning.models import VectorIndexSpec
from backend.vector_store.provisioning.pinecone import (
    PineconeInfrastructureProvider,
)


def test_pinecone_managed_index_provisioning() -> None:
    """Create and verify the dedicated RAGOps lifecycle test index."""
    load_dotenv()

    api_key = os.getenv("PINECONE_API_KEY")
    assert api_key, "PINECONE_API_KEY is not configured in .env."

    dimensions_value = os.getenv("OPENAI_EMBEDDING_DIMENSIONS")
    dimensions = int(dimensions_value) if dimensions_value else 1536

    cloud = os.getenv("PINECONE_CLOUD", "aws")
    region = os.getenv("PINECONE_REGION", "us-east-1")

    index_name = "ragops-test-lifecycle"
    namespace = "ragops-test-lifecycle"

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
        before = infrastructure.inspect_index(
            index_name=index_name,
        )

        assert not before.exists, (
            f"Test index {index_name!r} already exists. "
            "Inspect it in Pinecone or remove it before rerunning this "
            "first-provisioning test."
        )

        created = infrastructure.ensure_index(
            spec=spec,
        )

        assert created.exists
        assert created.index_name == index_name
        assert created.dimension == dimensions
        assert created.metric == "cosine"

        deadline = time.monotonic() + 60
        inspection = created

        while time.monotonic() < deadline:
            inspection = infrastructure.inspect_index(
                index_name=index_name,
            )

            if inspection.ready:
                break

            time.sleep(2)
        else:
            raise AssertionError(
                f"Pinecone index {index_name!r} did not become ready "
                "within 60 seconds."
            )

        assert inspection.exists
        assert inspection.ready
        assert inspection.dimension == dimensions
        assert inspection.metric == "cosine"

        print("\n" + "=" * 80)
        print("RAGOps Pinecone Managed Infrastructure Test")
        print("=" * 80)
        print(f"Index     : {index_name}")
        print(f"Namespace : {namespace}")
        print(f"Dimension : {dimensions}")
        print("Metric    : cosine")
        print()
        print("Status    : CREATED AND READY")
        print()
        print("The test intentionally does NOT delete the index.")
        print("Inspect the index in the Pinecone console before proceeding.")
        print("=" * 80)

    finally:
        infrastructure.close()