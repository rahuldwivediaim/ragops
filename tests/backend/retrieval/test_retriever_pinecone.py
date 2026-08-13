"""
Retriever + Pinecone integration test.

Verifies the production Retriever.retrieve() flow:

    query text
        ↓
    OpenAI embedding
        ↓
    Pinecone similarity search
        ↓
    retrieved metadata
        ↓
    actual chunk text
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from backend.embeddings.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)
from backend.retrieval.retriever import Retriever
from backend.vector_store.providers.pinecone_provider import (
    PineconeProvider,
)


def test_retriever_pinecone() -> None:
    """
    Test the production Retriever against Pinecone.
    """

    # --------------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------------

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv(
        "PINECONE_INDEX_NAME",
        "ragframeworkdev",
    )

    assert openai_api_key, "OPENAI_API_KEY is not configured in .env."

    assert pinecone_api_key, "PINECONE_API_KEY is not configured in .env."

    # --------------------------------------------------------------
    # Create providers
    # --------------------------------------------------------------

    embedding_provider = OpenAIEmbeddingProvider(
        api_key=openai_api_key,
        model_name="text-embedding-3-small",
        dimensions=1536,
    )

    vector_store = PineconeProvider(
        api_key=pinecone_api_key,
        index_name=pinecone_index_name,
        namespace="batch-test",
    )

    # --------------------------------------------------------------
    # Create production Retriever
    # --------------------------------------------------------------

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    try:
        # ----------------------------------------------------------
        # Query
        # ----------------------------------------------------------

        query = "What is the purpose of the employee leave policy?"

        # ----------------------------------------------------------
        # Execute production retrieval function
        # ----------------------------------------------------------

        results = retriever.retrieve(
            query=query,
            top_k=3,
        )

        # ----------------------------------------------------------
        # Verify results
        # ----------------------------------------------------------

        assert results, "Retriever returned no results."

        assert len(results) <= 3

        for result in results:
            assert "vector_id" in result
            assert "score" in result
            assert "metadata" in result

            assert result["vector_id"]
            assert result["score"] is not None

            metadata = result["metadata"]

            assert metadata, "Retrieved result contains no metadata."

            assert "document_id" in metadata
            assert "document_version_id" in metadata
            assert "chunk_id" in metadata
            assert "chunk_number" in metadata
            assert "filename" in metadata
            assert "text" in metadata

            # Most important verification:
            # actual chunk text is returned by the
            # production retrieval function.
            assert metadata["text"]

        # ----------------------------------------------------------
        # Display concise results
        # ----------------------------------------------------------

        print("\n" + "=" * 80)
        print("Retriever + Pinecone Test")
        print("=" * 80)

        print(f"Index       : {pinecone_index_name}")

        print("Namespace   : batch-test")

        print(f"Query       : {query}")

        print(f"Results     : {len(results)}")

        print("\nRetrieved Results")
        print("-" * 80)

        for index, result in enumerate(
            results,
            start=1,
        ):
            metadata = result["metadata"]

            chunk_text = str(metadata["text"]).replace("\n", " ")

            # Avoid huge console output.
            if len(chunk_text) > 120:
                chunk_text = chunk_text[:120] + "..."

            print(f"Result #{index}")

            print(f"  Score      : {result['score']:.6f}")

            print(f"  Vector ID  : {result['vector_id']}")

            print(f"  Chunk ID   : {metadata['chunk_id']}")

            print(f"  Chunk No.  : {metadata['chunk_number']}")

            print(f"  Filename   : {metadata['filename']}")

            print(f"  Text       : {chunk_text}")

        print("\nStatus      : PASSED")
        print("=" * 80)

    finally:
        vector_store.close()
        embedding_provider.close()
