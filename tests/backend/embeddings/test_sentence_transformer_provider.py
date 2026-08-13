"""
Unit tests for SentenceTransformerProvider.
"""

from pathlib import Path

from backend.embeddings.providers.sentence_transformer_provider import (
    SentenceTransformerProvider,
)


def test_sentence_transformer_provider() -> None:
    """
    Verify that SentenceTransformerProvider generates embeddings.
    """

    sample_file = Path("samples/sample.txt")

    assert sample_file.exists()

    text = sample_file.read_text(
        encoding="utf-8",
    )

    provider = SentenceTransformerProvider()

    result = provider.embed(text)

    print("\n" + "=" * 100)
    print("Sentence Transformer Provider")
    print("=" * 100)
    print(f"Provider      : {result.provider}")
    print(f"Model         : {result.model_name}")
    print(f"Dimensions    : {result.dimensions}")
    print(f"Vector Length : {result.vector_length}")

    print("\nFirst 20 values")
    print("-" * 100)

    for value in result.vector[:20]:
        print(value)

    print("=" * 100)

    assert result.provider == provider.provider_name

    assert result.model_name == provider.model_name

    assert result.dimensions == provider.dimensions

    assert result.vector_length == provider.dimensions

    assert result.vector_length > 0

    assert len(result.vector) == provider.dimensions
