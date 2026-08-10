"""
Integration test for OpenAIEmbeddingProvider.

This test makes a real request to the OpenAI Embeddings API.
The OPENAI_API_KEY and related settings are loaded from .env.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from backend.embeddings.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)


def test_openai_embedding_provider() -> None:
    """
    Verify that OpenAIEmbeddingProvider generates an embedding.
    """

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    assert api_key, (
        "OPENAI_API_KEY is not configured. "
        "Add it to the .env file before running this test."
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

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists(), (
        f"Sample file not found: {sample_file}"
    )

    text = sample_file.read_text(
        encoding="utf-8",
    )

    provider = OpenAIEmbeddingProvider(
        api_key=api_key,
        model_name=model_name,
        dimensions=dimensions,
    )

    result = provider.embed(text)

    print("\n" + "=" * 100)
    print("OpenAI Embedding Provider")
    print("=" * 100)
    print(f"Provider      : {result.provider}")
    print(f"Model         : {result.model_name}")
    print(f"Dimensions    : {result.dimensions}")
    print(f"Vector Length : {result.vector_length}")
    print(f"Version       : {result.embedding_version}")

    print("\nFirst 20 values")
    print("-" * 100)

    for value in result.vector[:20]:
        print(value)

    print("=" * 100)

    assert result.provider == "openai"

    assert result.model_name == model_name

    assert result.dimensions > 0

    assert result.vector_length == result.dimensions

    assert len(result.vector) == result.dimensions

    if dimensions is not None:
        assert result.dimensions == dimensions