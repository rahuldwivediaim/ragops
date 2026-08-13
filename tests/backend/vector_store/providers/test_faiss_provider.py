"""
Unit tests for FAISSProvider.

Verifies:
- Vector insertion
- Vector count
- Similarity search
- Metadata filtering
- Vector deletion
"""

from __future__ import annotations

from pathlib import Path

from backend.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerProvider,
)
from backend.vector_store.providers.faiss_provider import (
    FAISSProvider,
)


def test_faiss_provider() -> None:
    """
    Verify the complete local embedding-to-FAISS workflow.
    """

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists(), f"Sample file not found: {sample_file}"

    text = sample_file.read_text(
        encoding="utf-8",
    )

    embedding_provider = SentenceTransformerProvider()

    embedding_result = embedding_provider.embed(text)

    vector_store = FAISSProvider(
        dimensions=embedding_result.dimensions,
    )

    vector_id = "sample-document-chunk-001"

    metadata = {
        "document_id": "sample-document",
        "document_version_id": "version-1",
        "chunk_id": "chunk-001",
        "chunk_number": 1,
        "filename": sample_file.name,
        "provider": embedding_result.provider,
        "model_name": embedding_result.model_name,
        "embedding_version": embedding_result.embedding_version,
    }

    vector_store.upsert(
        vector_id=vector_id,
        vector=embedding_result.vector,
        metadata=metadata,
    )

    print("\n" + "=" * 100)
    print("FAISS Vector Store")
    print("=" * 100)

    print(f"Provider       : {vector_store.provider_name}")
    print(f"Dimensions     : {embedding_result.dimensions}")
    print(f"Embedding      : {embedding_result.model_name}")
    print(f"Vector ID      : {vector_id}")
    print(f"Record Count   : {vector_store.count()}")

    assert vector_store.count() == 1

    results = vector_store.query(
        vector=embedding_result.vector,
        top_k=5,
    )

    print("\nQuery Results")
    print("-" * 100)

    for result in results:
        print(f"Vector ID      : {result['vector_id']}")
        print(f"Score           : {result['score']}")
        print(f"Metadata        : {result['metadata']}")
        print("-" * 100)

    assert len(results) == 1

    result = results[0]

    assert result["vector_id"] == vector_id

    assert result["score"] > 0.99

    assert result["metadata"]["document_id"] == "sample-document"

    assert result["metadata"]["chunk_id"] == "chunk-001"

    filtered_results = vector_store.query(
        vector=embedding_result.vector,
        top_k=5,
        metadata_filter={
            "document_id": "sample-document",
        },
    )

    print("\nFiltered Results")
    print("-" * 100)

    for result in filtered_results:
        print(f"Vector ID      : {result['vector_id']}")
        print(f"Metadata        : {result['metadata']}")

    assert len(filtered_results) == 1

    non_matching_results = vector_store.query(
        vector=embedding_result.vector,
        top_k=5,
        metadata_filter={
            "document_id": "different-document",
        },
    )

    assert non_matching_results == []

    vector_store.delete(
        vector_ids=[vector_id],
    )

    print("\nAfter Delete")
    print("-" * 100)
    print(f"Record Count   : {vector_store.count()}")

    assert vector_store.count() == 0

    print("=" * 100)
