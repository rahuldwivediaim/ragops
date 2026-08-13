"""
Pinecone batch upsert integration test.

Verifies that all chunks from sample.txt can be embedded and
upserted into Pinecone in a single batch, with metadata attached
to every vector, including the original chunk text.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

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
    """

    # --------------------------------------------------------------
    # Load environment variables
    # --------------------------------------------------------------

    load_dotenv()

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv(
        "PINECONE_INDEX_NAME",
        "ragframeworkdev",
    )

    openai_api_key = os.getenv("OPENAI_API_KEY")

    assert pinecone_api_key, "PINECONE_API_KEY is not configured in .env."

    assert openai_api_key, "OPENAI_API_KEY is not configured in .env."

    # --------------------------------------------------------------
    # Step 1: Load sample document
    # --------------------------------------------------------------

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists(), f"Sample file not found: {sample_file}"

    text = sample_file.read_text(
        encoding="utf-8",
    )

    assert text.strip(), f"Sample file is empty: {sample_file}"

    # --------------------------------------------------------------
    # Step 2: Chunk document
    # --------------------------------------------------------------

    chunker = TextChunker()

    chunks = chunker.chunk(text)

    assert chunks, "No chunks were generated."

    # --------------------------------------------------------------
    # Step 3: Generate embeddings
    # --------------------------------------------------------------

    embedding_provider = OpenAIEmbeddingProvider(
        api_key=openai_api_key,
        model_name=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        ),
        dimensions=1536,
    )

    try:
        embeddings = embedding_provider.embed_batch(
            chunks,
        )

        assert len(embeddings) == len(chunks), (
            "Number of embeddings does not match number of chunks."
        )

        # ----------------------------------------------------------
        # Step 4: Create Pinecone provider
        # ----------------------------------------------------------

        namespace = "batch-test"

        vector_store = PineconeProvider(
            api_key=pinecone_api_key,
            index_name=pinecone_index_name,
            namespace=namespace,
        )

        try:
            # ------------------------------------------------------
            # Step 5: Build vector records
            # ------------------------------------------------------

            vectors: list[dict] = []

            for index, embedding in enumerate(embeddings):
                chunk_number = index + 1

                vector_id = f"rag-emp-001-version-1-chunk-{chunk_number:03d}"

                metadata = {
                    "document_id": "RAG-EMP-001",
                    "document_version_id": "1",
                    "chunk_id": (f"chunk-{chunk_number:03d}"),
                    "chunk_number": chunk_number,
                    "filename": sample_file.name,
                    "provider": embedding.provider,
                    "model_name": embedding.model_name,
                    "embedding_version": "1",
                    # Store the actual chunk text.
                    "text": chunks[index],
                }

                vectors.append(
                    {
                        "id": vector_id,
                        "values": embedding.vector,
                        "metadata": metadata,
                    }
                )

            # ------------------------------------------------------
            # Step 6: Validate vector records before upsert
            # ------------------------------------------------------

            assert len(vectors) == len(chunks)

            for index, vector in enumerate(vectors):
                assert vector["id"]
                assert vector["values"]
                assert vector["metadata"]

                metadata = vector["metadata"]

                assert metadata["document_id"] == ("RAG-EMP-001")

                assert metadata["document_version_id"] == "1"

                assert metadata["chunk_id"] == (f"chunk-{index + 1:03d}")

                assert metadata["chunk_number"] == (index + 1)

                assert metadata["filename"] == ("sample.txt")

                assert metadata["provider"] == "openai"

                assert metadata["model_name"] == ("text-embedding-3-small")

                assert metadata["embedding_version"] == "1"

                # Verify chunk text exists.
                assert "text" in metadata
                assert metadata["text"]

                # Verify the correct chunk text is associated
                # with the correct chunk number.
                assert metadata["text"] == chunks[index]

            # ------------------------------------------------------
            # Step 7: Batch upsert
            # ------------------------------------------------------

            vector_store.upsert_batch(
                vectors,
            )

            # ------------------------------------------------------
            # Step 8: Verify stored vector count
            # ------------------------------------------------------

            stored_count = vector_store.count()

            assert stored_count == len(vectors), (
                f"Expected {len(vectors)} vectors but found "
                f"{stored_count} in namespace '{namespace}'."
            )

            # ------------------------------------------------------
            # Step 9: Query vectors back
            # ------------------------------------------------------

            results = vector_store.query(
                vector=embeddings[0].vector,
                top_k=len(vectors),
            )

            assert len(results) == len(vectors), (
                f"Expected {len(vectors)} query results but received {len(results)}."
            )

            # ------------------------------------------------------
            # Step 10: Verify vector IDs
            # ------------------------------------------------------

            result_ids = {result["vector_id"] for result in results}

            expected_ids = {vector["id"] for vector in vectors}

            assert result_ids == expected_ids, (
                "Returned vector IDs do not match the vectors that were submitted."
            )

            # ------------------------------------------------------
            # Step 11: Verify metadata and chunk text
            # ------------------------------------------------------

            results_by_chunk_number = {}

            for result in results:
                metadata = result["metadata"]

                assert metadata["document_id"] == ("RAG-EMP-001")

                assert metadata["document_version_id"] == "1"

                assert metadata["filename"] == "sample.txt"

                assert metadata["provider"] == "openai"

                assert metadata["model_name"] == ("text-embedding-3-small")

                assert metadata["embedding_version"] == "1"

                assert "chunk_id" in metadata
                assert "chunk_number" in metadata

                # Verify text is returned from Pinecone metadata.
                assert "text" in metadata
                assert metadata["text"]

                chunk_number = metadata["chunk_number"]

                results_by_chunk_number[chunk_number] = result

            # ------------------------------------------------------
            # Step 12: Verify every chunk has the correct text
            # ------------------------------------------------------

            assert len(results_by_chunk_number) == len(chunks)

            for chunk_number, chunk in enumerate(
                chunks,
                start=1,
            ):
                assert chunk_number in (results_by_chunk_number)

                result = results_by_chunk_number[chunk_number]

                metadata = result["metadata"]

                assert metadata["chunk_id"] == (f"chunk-{chunk_number:03d}")

                assert metadata["text"] == chunk

            # ------------------------------------------------------
            # Display concise result
            # ------------------------------------------------------

            print("\n" + "=" * 80)
            print("Pinecone Batch Upsert Test")
            print("=" * 80)

            print(f"Index              : {pinecone_index_name}")

            print(f"Namespace          : {namespace}")

            print(f"Chunks             : {len(chunks)}")

            print(f"Embeddings         : {len(embeddings)}")

            print(f"Vectors submitted  : {len(vectors)}")

            print(f"Vectors stored     : {stored_count}")

            print("Embedding provider : openai")

            print("Embedding model    : text-embedding-3-small")

            print("Dimensions         : 1536")

            print("Chunk text stored  : YES")

            print("\nSample vector metadata")
            print("-" * 80)

            sample_result = results_by_chunk_number[1]

            print(f"Vector ID : {sample_result['vector_id']}")

            sample_metadata = sample_result["metadata"]

            for key, value in sample_metadata.items():
                if key == "text":
                    # Avoid printing the complete chunk.
                    text_value = str(value)

                    if len(text_value) > 120:
                        text_value = text_value[:120] + "..."

                    print(f"{key:<22}: {text_value}")
                else:
                    print(f"{key:<22}: {value}")

            print("\nStatus               : PASSED")
            print("=" * 80)

        finally:
            vector_store.close()

    finally:
        # Close the embedding provider as well.
        embedding_provider.close()
