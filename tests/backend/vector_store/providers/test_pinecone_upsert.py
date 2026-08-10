"""
Pinecone upsert integration test.

This test intentionally performs ONLY the upsert operation.

The inserted vector is not deleted so it can be inspected
in the Pinecone console after the test completes.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from backend.embeddings.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)
from backend.vector_store.providers.pinecone_provider import (
    PineconeProvider,
)


def test_pinecone_upsert() -> None:
    """
    Generate an OpenAI embedding and upsert it into Pinecone.

    This test does not query or delete the vector.
    """

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    assert openai_api_key, (
        "OPENAI_API_KEY is not configured in .env."
    )

    assert pinecone_api_key, (
        "PINECONE_API_KEY is not configured in .env."
    )

    model_name = os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )

    dimensions_value = os.getenv(
        "OPENAI_EMBEDDING_DIMENSIONS",
    )

    dimensions = (
        int(dimensions_value)
        if dimensions_value
        else None
    )

    index_name = os.getenv(
        "PINECONE_INDEX",
        "ragframeworkdev",
    )

    namespace = os.getenv(
        "PINECONE_NAMESPACE",
        "default",
    )

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists(), (
        f"Sample file not found: {sample_file}"
    )

    text = sample_file.read_text(
        encoding="utf-8",
    )

    embedding_provider = OpenAIEmbeddingProvider(
        api_key=openai_api_key,
        model_name=model_name,
        dimensions=dimensions,
    )

    # Initialize to None so the finally block can safely
    # determine whether the Pinecone provider was created.
    vector_store = None

    try:
        # ----------------------------------------------------------
        # Step 1: Generate OpenAI embedding
        # ----------------------------------------------------------

        embedding_result = embedding_provider.embed(
            text,
        )

        # ----------------------------------------------------------
        # Step 2: Create Pinecone provider
        # ----------------------------------------------------------

        vector_store = PineconeProvider(
            api_key=pinecone_api_key,
            index_name=index_name,
            namespace=namespace,
        )

        # ----------------------------------------------------------
        # Step 3: Create a unique vector ID
        # ----------------------------------------------------------

        vector_id = (
            f"test-document-{uuid.uuid4().hex}"
        )

        metadata = {
            "document_id": "sample-document",
            "document_version_id": "version-1",
            "chunk_id": "chunk-001",
            "chunk_number": 1,
            "filename": sample_file.name,
            "provider": embedding_result.provider,
            "model_name": embedding_result.model_name,
            "embedding_version": (
                embedding_result.embedding_version
            ),
        }

        # ----------------------------------------------------------
        # Step 4: Upsert into Pinecone
        # ----------------------------------------------------------

        vector_store.upsert(
            vector_id=vector_id,
            vector=embedding_result.vector,
            metadata=metadata,
        )

        # ----------------------------------------------------------
        # Display results
        # ----------------------------------------------------------

        print("\n" + "=" * 100)
        print("Pinecone Upsert Test")
        print("=" * 100)

        print(
            f"Provider        : "
            f"{vector_store.provider_name}"
        )

        print(
            f"Index           : "
            f"{vector_store.index_name}"
        )

        print(
            f"Namespace       : "
            f"{vector_store.namespace}"
        )

        print(
            f"Embedding Model : "
            f"{embedding_result.model_name}"
        )

        print(
            f"Dimensions      : "
            f"{embedding_result.dimensions}"
        )

        print(
            f"Vector ID       : "
            f"{vector_id}"
        )

        print("\nMetadata")
        print("-" * 100)

        for key, value in metadata.items():
            print(f"{key:<24}: {value}")

        print("\nStatus")
        print("-" * 100)

        print(
            "Vector successfully submitted "
            "to Pinecone."
        )

        print(
            "The vector is intentionally NOT deleted."
        )

        print("=" * 100)

    finally:
        # ----------------------------------------------------------
        # Release HTTP resources.
        # ----------------------------------------------------------

        embedding_provider.close()

        if vector_store is not None:
            vector_store.close()