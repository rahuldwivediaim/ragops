"""
Sentence Transformer batch embedding integration test.

Verifies that all chunks produced from the sample document can be
embedded in a single batch and that one embedding is returned for
each chunk.
"""

from __future__ import annotations

from pathlib import Path

from backend.document_processing.chunker import TextChunker
from backend.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerProvider,
)


def test_sentence_transformer_batch_embedding() -> None:
    """
    Chunk the sample document and generate embeddings for all chunks.
    """

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists(), (
        f"Sample file not found: {sample_file}"
    )

    text = sample_file.read_text(
        encoding="utf-8",
    )

    # --------------------------------------------------------------
    # Step 1: Create chunks
    # --------------------------------------------------------------

    chunker = TextChunker()

    chunks = chunker.chunk(
        text,
    )

    assert chunks, "No chunks were generated."

    # --------------------------------------------------------------
    # Step 2: Chunks are already strings
    # --------------------------------------------------------------

    chunk_texts = chunks

    # --------------------------------------------------------------
    # Step 3: Create embedding provider
    # --------------------------------------------------------------

    provider = SentenceTransformerProvider()

    # --------------------------------------------------------------
    # Step 4: Generate embeddings in one batch
    # --------------------------------------------------------------

    results = provider.embed_batch(
        chunk_texts,
    )

    # --------------------------------------------------------------
    # Step 5: Verify results
    # --------------------------------------------------------------

    assert len(results) == len(chunks)

    for result in results:
        assert result.provider == (
            provider.provider_name
        )

        assert result.model_name == (
            provider.model_name
        )

        assert result.dimensions == 384

        assert len(result.vector) == 384

    # --------------------------------------------------------------
    # Display concise test information
    # --------------------------------------------------------------

    print("\n" + "=" * 80)
    print("Sentence Transformer Batch Embedding Test")
    print("=" * 80)

    print(f"Chunks generated       : {len(chunks)}")
    print(f"Embeddings generated   : {len(results)}")
    print(f"Provider               : {provider.provider_name}")
    print(f"Model                  : {provider.model_name}")
    print(f"Dimensions             : {results[0].dimensions}")

    print("\nFirst 3 chunks")
    print("-" * 80)

    for index, chunk in enumerate(
        chunks[:3],
        start=1,
    ):
        print(
            f"Chunk {index}: "
            f"{len(chunk)} characters"
        )

    if len(chunks) > 6:
        print("\n...")

    print("\nLast 3 chunks")
    print("-" * 80)

    start_index = max(
        0,
        len(chunks) - 3,
    )

    for index, chunk in enumerate(
        chunks[start_index:],
        start=start_index + 1,
    ):
        print(
            f"Chunk {index}: "
            f"{len(chunk)} characters"
        )

    print("\nResult Summary")
    print("-" * 80)

    print(
        f"Every chunk has a corresponding "
        f"{results[0].dimensions}-dimensional embedding."
    )

    print("=" * 80)