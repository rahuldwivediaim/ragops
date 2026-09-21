"""
Real Pinecone namespace isolation integration test.

This test verifies that RAGOps can operate inside its own namespace
within an existing Pinecone index without affecting another namespace.

IMPORTANT:
- The test uses the existing `ragops-test-lifecycle` index.
- It creates vectors in two isolated namespaces.
- The vectors are intentionally NOT deleted.
- The Pinecone index is intentionally NOT deleted.
- The resulting state can be inspected manually in the Pinecone console.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from backend.vector_store.providers.pinecone_provider import PineconeProvider


INDEX_NAME = "ragops-test-lifecycle"
CUSTOMER_NAMESPACE = "customer-existing"
RAGOPS_NAMESPACE = "ragops-hr"

CUSTOMER_VECTOR_ID = "customer-test-vector"
RAGOPS_VECTOR_ID = "ragops-test-vector"

VECTOR_DIMENSIONS = 1536


def _build_vector(seed: float) -> list[float]:
    """Build a deterministic vector with the required Pinecone dimension."""
    return [seed] * VECTOR_DIMENSIONS


def test_pinecone_namespace_isolation() -> None:
    """
    Verify that RAGOps vectors remain isolated inside ragops-hr.

    The test writes one vector into a customer namespace and one vector
    into the RAGOps namespace, then verifies that each provider can see
    only the vector belonging to its configured namespace.
    """
    load_dotenv()

    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    assert pinecone_api_key, (
        "PINECONE_API_KEY is not configured in .env."
    )

    customer_store = PineconeProvider(
        api_key=pinecone_api_key,
        index_name=INDEX_NAME,
        namespace=CUSTOMER_NAMESPACE,
    )

    ragops_store = PineconeProvider(
        api_key=pinecone_api_key,
        index_name=INDEX_NAME,
        namespace=RAGOPS_NAMESPACE,
    )

    try:
        customer_vector = _build_vector(0.1)
        ragops_vector = _build_vector(0.2)

        customer_metadata = {
            "owner": "customer-test",
            "namespace": CUSTOMER_NAMESPACE,
            "purpose": "namespace-isolation-test",
        }

        ragops_metadata = {
            "ragops_managed": True,
            "namespace": RAGOPS_NAMESPACE,
            "purpose": "namespace-isolation-test",
        }

        # --------------------------------------------------------------
        # Step 1: Write a vector to the customer namespace.
        # --------------------------------------------------------------

        customer_store.upsert(
            vector_id=CUSTOMER_VECTOR_ID,
            vector=customer_vector,
            metadata=customer_metadata,
        )

        # --------------------------------------------------------------
        # Step 2: Write a vector to the RAGOps namespace.
        # --------------------------------------------------------------

        ragops_store.upsert(
            vector_id=RAGOPS_VECTOR_ID,
            vector=ragops_vector,
            metadata=ragops_metadata,
        )

        # --------------------------------------------------------------
        # Step 3: Verify namespace-specific counts.
        # --------------------------------------------------------------

        customer_count = customer_store.count()
        ragops_count = ragops_store.count()

        assert customer_count >= 1
        assert ragops_count >= 1

        # --------------------------------------------------------------
        # Step 4: Query the customer namespace.
        # --------------------------------------------------------------

        customer_results = customer_store.query(
            vector=customer_vector,
            top_k=5,
        )

        assert customer_results
        assert any(
            result["vector_id"] == CUSTOMER_VECTOR_ID
            for result in customer_results
        )

        assert not any(
            result["vector_id"] == RAGOPS_VECTOR_ID
            for result in customer_results
        )

        # --------------------------------------------------------------
        # Step 5: Query the RAGOps namespace.
        # --------------------------------------------------------------

        ragops_results = ragops_store.query(
            vector=ragops_vector,
            top_k=5,
        )

        assert ragops_results
        assert any(
            result["vector_id"] == RAGOPS_VECTOR_ID
            for result in ragops_results
        )

        assert not any(
            result["vector_id"] == CUSTOMER_VECTOR_ID
            for result in ragops_results
        )

        # --------------------------------------------------------------
        # Step 6: Display the isolation result.
        # --------------------------------------------------------------

        print("\n" + "=" * 80)
        print("RAGOps Pinecone Namespace Isolation Test")
        print("=" * 80)

        print(f"Index              : {INDEX_NAME}")
        print()

        print(f"Customer Namespace : {CUSTOMER_NAMESPACE}")
        print(f"Customer Vector ID  : {CUSTOMER_VECTOR_ID}")
        print(f"Customer Count      : {customer_count}")
        print("Customer Query      : PASS")
        print()

        print(f"RAGOps Namespace    : {RAGOPS_NAMESPACE}")
        print(f"RAGOps Vector ID     : {RAGOPS_VECTOR_ID}")
        print(f"RAGOps Count         : {ragops_count}")
        print("RAGOps Query         : PASS")
        print()

        print("Cross-Namespace Isolation : PASS")
        print()
        print("The test vectors are intentionally NOT deleted.")
        print("The Pinecone index is intentionally NOT deleted.")
        print()
        print("Inspect the two namespaces in the Pinecone console.")
        print("=" * 80)

    finally:
        customer_store.close()
        ragops_store.close()