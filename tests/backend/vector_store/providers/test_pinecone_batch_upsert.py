"""
Pinecone batch upsert integration test.

Verifies that all chunks from sample.txt can be embedded and
upserted into Pinecone in a single batch, with metadata attached
to every vector, including the original chunk text.

The test uses the current application configuration for the Pinecone
index and creates a unique namespace for every test execution so
that previous test runs cannot contaminate the vector count.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from backend.common.config.loader import load_settings
from backend.document_processing.chunker import TextChunker
from backend.embeddings.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)
from backend.vector_store.providers.pinecone_provider import (
    PineconeProvider,
)


def test_pinecone_batch_upsert() -> None:
    """
    Generate embeddings for all chunks and batch upsert them
    into Pinecone with chunk text stored in metadata.

    A unique namespace is used for every execution so the test
    remains isolated from previous runs and other integration tests.
    """

    # --------------------------------------------------------------
    # Step 1: Load configuration
    # --------------------------------------------------------------

    load_dotenv()

    settings = load_settings()

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    assert pinecone_api_key, (
        "PINECONE_API_KEY is not configured in .env."
    )

    assert openai_api_key, (
        "OPENAI_API_KEY is not configured in .env."
    )

    pinecone_index_name = settings.vector_store.index_name

    assert pinecone_index_name, (
        "Pinecone index name is not configured."
    )

    # --------------------------------------------------------------
    # Step 2: Create isolated test namespace
    # --------------------------------------------------------------

    namespace = f"test-batch-{uuid.uuid4().hex[:12]}"

    # --------------------------------------------------------------
    # Step 3: Load sample document
    # --------------------------------------------------------------

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists(), (
        f"Sample file not found: {sample_file}"
    )

    text = sample_file.read_text(
        encoding="utf-8",
    )

    assert text.strip(), (
        f"Sample file is empty: {sample_file}"
    )

    # --------------------------------------------------------------
    # Step 4: Chunk document
    # --------------------------------------------------------------

    chunker = TextChunker()

    chunks = chunker.chunk(text)

    assert chunks, (
        "No chunks were generated."
    )

    # --------------------------------------------------------------
    # Step 5: Generate embeddings
    # --------------------------------------------------------------

    embedding_provider = OpenAIEmbeddingProvider(
        api_key=openai_api_key,
        model_name=settings.embeddings.model,
        dimensions=settings.embeddings.dimensions or 1536,
    )

    vector_store: PineconeProvider | None = None
    vectors: list[dict] = []

    try:
        embeddings = embedding_provider.embed_batch(
            chunks,
        )

        assert len(embeddings) == len(chunks), (
            "Number of embeddings does not match number of chunks."
        )

        # ----------------------------------------------------------
        # Step 6: Create Pinecone provider
        # ----------------------------------------------------------

        vector_store = PineconeProvider(
            api_key=pinecone_api_key,
            index_name=pinecone_index_name,
            namespace=namespace,
        )

        # ----------------------------------------------------------
        # Step 7: Build vector records
        # ----------------------------------------------------------

        for index, embedding in enumerate(embeddings):
            chunk_number = index + 1

            vector_id = (
                f"rag-emp-001-version-1-chunk-{chunk_number:03d}"
            )

            metadata = {
                "document_id": "RAG-EMP-001",
                "document_version_id": "1",
                "chunk_id": f"chunk-{chunk_number:03d}",
                "chunk_number": chunk_number,
                "filename": sample_file.name,
                "provider": embedding.provider,
                "model_name": embedding.model_name,
                "embedding_version": "1",
                "text": chunks[index],
            }

            vectors.append(
                {
                    "id": vector_id,
                    "values": embedding.vector,
                    "metadata": metadata,
                }
            )

        # ----------------------------------------------------------
        # Step 8: Validate vector records before upsert
        # ----------------------------------------------------------

        assert len(vectors) == len(chunks)

        for index, vector in enumerate(vectors):
            assert vector["id"]
            assert vector["values"]
            assert vector["metadata"]

            metadata = vector["metadata"]

            assert metadata["document_id"] == "RAG-EMP-001"

            assert metadata["document_version_id"] == "1"

            assert metadata["chunk_id"] == (
                f"chunk-{index + 1:03d}"
            )

            assert metadata["chunk_number"] == index + 1

            assert metadata["filename"] == "sample.txt"

            assert metadata["provider"] == "openai"

            assert metadata["model_name"] == (
                settings.embeddings.model
            )

            assert metadata["embedding_version"] == "1"

            assert "text" in metadata
            assert metadata["text"]

            assert metadata["text"] == chunks[index]

        # ----------------------------------------------------------
        # Step 9: Batch upsert
        # ----------------------------------------------------------

        vector_store.upsert_batch(
            vectors,
        )

        # ----------------------------------------------------------
        # Step 10: Verify stored vector count
        # ----------------------------------------------------------

        stored_count = vector_store.count()

        assert stored_count == len(vectors), (
            f"Expected {len(vectors)} vectors but found "
            f"{stored_count} in namespace '{namespace}'."
        )

        # ----------------------------------------------------------
        # Step 11: Query vectors back
        # ----------------------------------------------------------

        results = vector_store.query(
            vector=embeddings[0].vector,
            top_k=len(vectors),
        )

        assert len(results) == len(vectors), (
            f"Expected {len(vectors)} query results "
            f"but received {len(results)}."
        )

        # ----------------------------------------------------------
        # Step 12: Verify vector IDs
        # ----------------------------------------------------------

        result_ids = {
            result["vector_id"]
            for result in results
        }

        expected_ids = {
            vector["id"]
            for vector in vectors
        }

        assert result_ids == expected_ids, (
            "Returned vector IDs do not match the vectors "
            "that were submitted."
        )

        # ----------------------------------------------------------
        # Step 13: Verify metadata and chunk text
        # ----------------------------------------------------------

        results_by_chunk_number: dict[int, dict] = {}

        for result in results:
            metadata = result["metadata"]

            assert metadata["document_id"] == "RAG-EMP-001"

            assert metadata["document_version_id"] == "1"

            assert metadata["filename"] == "sample.txt"

            assert metadata["provider"] == "openai"

            assert metadata["model_name"] == (
                settings.embeddings.model
            )

            assert metadata["embedding_version"] == "1"

            assert "chunk_id" in metadata
            assert "chunk_number" in metadata

            assert "text" in metadata
            assert metadata["text"]

            chunk_number = int(
                metadata["chunk_number"]
            )

            results_by_chunk_number[chunk_number] = result

        # ----------------------------------------------------------
        # Step 14: Verify every chunk has correct text
        # ----------------------------------------------------------

        assert len(results_by_chunk_number) == len(chunks)

        for chunk_number, chunk in enumerate(
            chunks,
            start=1,
        ):
            assert chunk_number in results_by_chunk_number

            result = results_by_chunk_number[chunk_number]

            metadata = result["metadata"]

            assert metadata["chunk_id"] == (
                f"chunk-{chunk_number:03d}"
            )

            assert metadata["text"] == chunk

        # ----------------------------------------------------------
        # Step 15: Display result
        # ----------------------------------------------------------

        print("\n" + "=" * 80)
        print("Pinecone Batch Upsert Test")
        print("=" * 80)

        print(
            f"Index              : {pinecone_index_name}"
        )

        print(
            f"Namespace          : {namespace}"
        )

        print(
            f"Chunks             : {len(chunks)}"
        )

        print(
            f"Embeddings         : {len(embeddings)}"
        )

        print(
            f"Vectors submitted  : {len(vectors)}"
        )

        print(
            f"Vectors stored     : {stored_count}"
        )

        print(
            "Embedding provider : "
            f"{settings.embeddings.provider.value}"
        )

        print(
            f"Embedding model    : {settings.embeddings.model}"
        )

        print(
            "Dimensions         : "
            f"{settings.embeddings.dimensions}"
        )

        print(
            "Chunk text stored  : YES"
        )

        print("\nSample vector metadata")
        print("-" * 80)

        sample_result = results_by_chunk_number[1]

        print(
            f"Vector ID : "
            f"{sample_result['vector_id']}"
        )

        sample_metadata = sample_result["metadata"]

        for key, value in sample_metadata.items():
            if key == "text":
                text_value = str(value)

                if len(text_value) > 120:
                    text_value = text_value[:120] + "..."

                print(
                    f"{key:<22}: {text_value}"
                )
            else:
                print(
                    f"{key:<22}: {value}"
                )

        print("\nStatus               : PASSED")
        print("=" * 80)

    finally:
        # ----------------------------------------------------------
        # Cleanup
        # ----------------------------------------------------------
        #
        # PineconeProvider supports deleting vectors by ID.
        # We deliberately delete only the vectors created by this
        # test. We do NOT delete the namespace or the index.
        #

        if vector_store is not None:
            try:
                vector_ids = [
                    vector["id"]
                    for vector in vectors
                ]

                if vector_ids:
                    vector_store.delete(
                        vector_ids,
                    )

            finally:
                vector_store.close()

        embedding_provider.close()