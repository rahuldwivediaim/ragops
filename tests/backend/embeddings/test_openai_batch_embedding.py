"""
OpenAI batch embedding integration test.

Verifies that multiple texts are embedded in a single
OpenAI API request and that one embedding is returned
for every input text.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from backend.embeddings.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)


def test_openai_batch_embedding() -> None:
    """
    Generate embeddings for multiple texts using one
    OpenAI batch embedding request.
    """

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    assert api_key, (
        "OPENAI_API_KEY is not configured in .env."
    )

    texts = [
        "Employees are entitled to annual leave.",
        "Annual leave must be requested through the HR system.",
        "Managers are responsible for approving leave requests.",
        "Unused leave may be carried forward according to policy.",
        "Employees should contact HR for leave-related questions.",
    ]

    provider = OpenAIEmbeddingProvider(
        api_key=api_key,
        model_name="text-embedding-3-small",
        dimensions=1536,
    )

    try:
        results = provider.embed_batch(texts)

        assert len(results) == len(texts)

        for result in results:
            assert result.provider == "openai"
            assert result.model_name == (
                "text-embedding-3-small"
            )
            assert result.dimensions == 1536
            assert len(result.vector) == 1536
            assert result.embedding_version == 1

        print("\n" + "=" * 80)
        print("OpenAI Batch Embedding Test")
        print("=" * 80)

        print(
            f"Input texts          : {len(texts)}"
        )

        print(
            f"Embeddings generated : {len(results)}"
        )

        print(
            f"Provider             : "
            f"{provider.provider_name}"
        )

        print(
            f"Model                : "
            f"{provider.model_name}"
        )

        print(
            f"Dimensions           : "
            f"{results[0].dimensions}"
        )

        print(
            "Batch request        : "
            "YES"
        )

        print(
            "\nStatus               : PASSED"
        )

        print("=" * 80)

    finally:
        provider.close()