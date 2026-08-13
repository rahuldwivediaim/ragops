"""
Tests for the reranker factory.
"""

from unittest.mock import patch

import pytest

from backend.reranking.reranker_factory import (
    RerankerFactory,
)


def test_factory_creates_cohere_provider() -> None:
    """
    Verify that the factory creates a Cohere provider.
    """

    with patch(
        "backend.reranking.reranker_factory.CohereRerankerProvider"
    ) as mock_provider:
        provider = RerankerFactory.create(
            provider="cohere",
            api_key="test-api-key",
        )

        mock_provider.assert_called_once_with(
            api_key="test-api-key",
        )

        assert provider is mock_provider.return_value


def test_factory_creates_cohere_provider_with_custom_model() -> None:
    """
    Verify that the factory passes a custom model to Cohere.
    """

    with patch(
        "backend.reranking.reranker_factory.CohereRerankerProvider"
    ) as mock_provider:
        provider = RerankerFactory.create(
            provider="cohere",
            api_key="test-api-key",
            model_name="rerank-v4.0-pro",
        )

        mock_provider.assert_called_once_with(
            api_key="test-api-key",
            model_name="rerank-v4.0-pro",
        )

        assert provider is mock_provider.return_value


def test_factory_is_case_insensitive() -> None:
    """
    Verify that provider names are case-insensitive.
    """

    with patch(
        "backend.reranking.reranker_factory.CohereRerankerProvider"
    ) as mock_provider:
        RerankerFactory.create(
            provider="CoHeRe",
            api_key="test-api-key",
        )

        mock_provider.assert_called_once_with(
            api_key="test-api-key",
        )


def test_factory_strips_provider_name() -> None:
    """
    Verify that whitespace around the provider name is ignored.
    """

    with patch(
        "backend.reranking.reranker_factory.CohereRerankerProvider"
    ) as mock_provider:
        RerankerFactory.create(
            provider="  cohere  ",
            api_key="test-api-key",
        )

        mock_provider.assert_called_once_with(
            api_key="test-api-key",
        )


def test_factory_rejects_unsupported_provider() -> None:
    """
    Verify that unsupported providers are rejected.
    """

    with pytest.raises(
        ValueError,
        match="Unsupported reranker provider: unknown",
    ):
        RerankerFactory.create(
            provider="unknown",
            api_key="test-api-key",
        )
