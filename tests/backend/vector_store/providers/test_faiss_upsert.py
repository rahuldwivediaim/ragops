"""
FAISS batch ingestion integration test.

Verifies that multiple document chunks can be embedded and stored
in FAISS with the expected metadata.
"""

from __future__ import annotations

from pathlib import Path

from backend.document_processing.chunker import TextChunker
from backend.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerProvider,
)
from backend.vector_store.providers.faiss_provider import FAISSProvider


def test_faiss_batch_upsert() -> None:
    """
    Generate embeddings for all document chunks and store them
    individually in FAISS.
    """

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists(), f"Sample file not found: {sample_file}"

    text = sample_file.read_text(
        encoding="utf-8",
    )

    # --------------------------------------------------------------
    # Step 1: Chunk document
    # --------------------------------------------------------------

    chunker = TextChunker()

    chunks = chunker.chunk(text)

    assert chunks, "No chunks were generated."

    # --------------------------------------------------------------
    # Step 2: Generate embeddings
    # --------------------------------------------------------------

    embedding_provider = SentenceTransformerProvider()

    embeddings = embedding_provider.embed_batch(chunks)

    assert len(embeddings) == len(chunks)

    # --------------------------------------------------------------
    # Step 3: Create FAISS provider
    # --------------------------------------------------------------

    vector_store = FAISSProvider(
        dimensions=384,
    )

    # --------------------------------------------------------------
    # Step 4: Store each embedding with metadata
    # --------------------------------------------------------------

    for index, embedding in enumerate(embeddings):
        vector_id = f"rag-emp-001-version-1-chunk-{index + 1:03d}"

        metadata = {
            "document_id": "RAG-EMP-001",
            "document_version_id": "1",
            "chunk_id": f"chunk-{index + 1:03d}",
            "chunk_number": index + 1,
            "filename": sample_file.name,
            "provider": embedding.provider,
            "model_name": embedding.model_name,
            "embedding_version": "1",
        }

        vector_store.upsert(
            vector_id=vector_id,
            vector=embedding.vector,
            metadata=metadata,
        )

    # --------------------------------------------------------------
    # Step 5: Verify vector count
    # --------------------------------------------------------------

    assert vector_store.count() == len(chunks)

    # --------------------------------------------------------------
    # Step 6: Verify metadata for every vector
    # --------------------------------------------------------------

    query_embedding = embeddings[0]

    results = vector_store.query(
        vector=query_embedding.vector,
        top_k=len(chunks),
    )

    assert results

    result_ids = {result["vector_id"] for result in results}

    expected_ids = {
        f"rag-emp-001-version-1-chunk-{index + 1:03d}" for index in range(len(chunks))
    }

    assert result_ids == expected_ids

    for result in results:
        metadata = result["metadata"]

        assert metadata["document_id"] == "RAG-EMP-001"
        assert metadata["document_version_id"] == "1"
        assert metadata["filename"] == "sample.txt"

        assert metadata["provider"] == (embedding_provider.provider_name)

        assert metadata["model_name"] == (embedding_provider.model_name)

        assert "chunk_id" in metadata
        assert "chunk_number" in metadata
        assert "embedding_version" in metadata

    # --------------------------------------------------------------
    # Display concise result
    # --------------------------------------------------------------

    print("\n" + "=" * 80)
    print("FAISS Batch Upsert Test")
    print("=" * 80)

    print(f"Chunks generated : {len(chunks)}")
    print(f"Embeddings       : {len(embeddings)}")
    print(f"FAISS vectors    : {vector_store.count()}")
    print(f"Dimensions       : {vector_store.dimensions}")
    print(f"Provider         : {embedding_provider.provider_name}")
    print(f"Model            : {embedding_provider.model_name}")

    print("\nSample stored metadata")
    print("-" * 80)

    first_result = results[0]

    print(f"Vector ID : {first_result['vector_id']}")

    for key, value in first_result["metadata"].items():
        print(f"{key:<22}: {value}")

    print("=" * 80)
