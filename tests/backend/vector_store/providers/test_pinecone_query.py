"""
Pinecone query integration test.

This test performs a read-only similarity search against the
existing vectors in Pinecone.

It does not insert or delete any vectors.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from backend.embeddings.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)
from backend.vector_store.providers.pinecone_provider import (
    PineconeProvider,
)


def test_pinecone_query() -> None:
    """
    Generate an OpenAI embedding and query existing Pinecone vectors.
    """

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    assert openai_api_key, "OPENAI_API_KEY is not configured in .env."

    assert pinecone_api_key, "PINECONE_API_KEY is not configured in .env."

    model_name = os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )

    dimensions_value = os.getenv(
        "OPENAI_EMBEDDING_DIMENSIONS",
    )

    dimensions = int(dimensions_value) if dimensions_value else None

    index_name = os.getenv(
        "PINECONE_INDEX",
        "ragframeworkdev",
    )

    namespace = os.getenv(
        "PINECONE_NAMESPACE",
        "default",
    )

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists(), f"Sample file not found: {sample_file}"

    text = sample_file.read_text(
        encoding="utf-8",
    )

    embedding_provider = OpenAIEmbeddingProvider(
        api_key=openai_api_key,
        model_name=model_name,
        dimensions=dimensions,
    )

    vector_store = PineconeProvider(
        api_key=pinecone_api_key,
        index_name=index_name,
        namespace=namespace,
    )

    try:
        # ----------------------------------------------------------
        # Step 1: Generate query embedding
        # ----------------------------------------------------------

        embedding_result = embedding_provider.embed(text)

        # ----------------------------------------------------------
        # Step 2: Query existing Pinecone vectors
        # ----------------------------------------------------------

        results = vector_store.query(
            vector=embedding_result.vector,
            top_k=3,
        )

        # ----------------------------------------------------------
        # Display results
        # ----------------------------------------------------------

        print("\n" + "=" * 100)
        print("Pinecone Query Test")
        print("=" * 100)

        print(f"Index           : {index_name}")
        print(f"Namespace       : {namespace}")
        print(f"Query Model     : {model_name}")
        print(f"Query Dimensions: {embedding_result.dimensions}")
        print(f"Results Found   : {len(results)}")

        print("\nQuery Results")
        print("-" * 100)

        for position, result in enumerate(
            results,
            start=1,
        ):
            print(f"\nResult #{position}")
            print(f"Vector ID : {result['vector_id']}")
            print(f"Score     : {result['score']}")

            print("Metadata:")
            for key, value in result["metadata"].items():
                print(f"  {key:<22}: {value}")

        print("=" * 100)

        # ----------------------------------------------------------
        # Assertions
        # ----------------------------------------------------------

        assert results, "No vectors were returned from Pinecone."

        assert len(results) <= 3

        for result in results:
            assert result["vector_id"]

            assert result["score"] >= 0.0

            assert "document_id" in result["metadata"]

            assert "chunk_id" in result["metadata"]

            assert "filename" in result["metadata"]

    finally:
        embedding_provider.close()
        vector_store.close()
