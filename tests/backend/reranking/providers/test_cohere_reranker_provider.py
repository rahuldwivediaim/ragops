"""
Tests for the Cohere reranker provider.

These tests mock the Cohere SDK and do not make
network requests or require a Cohere API key.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from backend.reranking.models import RerankResult
from backend.reranking.providers.cohere_reranker_provider import (
    CohereRerankerProvider,
)


COHERE_CLIENT_PATH = (
    "backend.reranking.providers.cohere_reranker_provider.cohere.ClientV2"
)


def create_mock_response(
    results: list[tuple[int, float]],
) -> SimpleNamespace:
    """
    Create a mock response matching the Cohere rerank response
    structure used by the provider.
    """

    mock_results = [
        SimpleNamespace(
            index=index,
            relevance_score=score,
        )
        for index, score in results
    ]

    return SimpleNamespace(
        results=mock_results,
    )


def test_provider_initialization() -> None:
    """
    Verify that the Cohere provider initializes correctly.
    """

    with patch(
        COHERE_CLIENT_PATH,
    ) as mock_client:
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        mock_client.assert_called_once_with(
            api_key="test-api-key",
        )

        assert provider.provider_name == "cohere"
        assert provider.model_name == "rerank-v4.0-fast"


def test_provider_accepts_custom_model() -> None:
    """
    Verify that a custom reranker model can be configured.
    """

    with patch(
        COHERE_CLIENT_PATH,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
            model_name="rerank-v4.0-pro",
        )

        assert provider.model_name == "rerank-v4.0-pro"


def test_empty_api_key_raises_error() -> None:
    """
    Verify that an empty API key is rejected.
    """

    with pytest.raises(
        ValueError,
        match="Cohere API key cannot be empty",
    ):
        CohereRerankerProvider(
            api_key="",
        )


def test_empty_model_name_raises_error() -> None:
    """
    Verify that an empty model name is rejected.
    """

    with pytest.raises(
        ValueError,
        match="Cohere reranker model name cannot be empty",
    ):
        CohereRerankerProvider(
            api_key="test-api-key",
            model_name="",
        )


def test_empty_query_raises_error() -> None:
    """
    Verify that an empty query is rejected.
    """

    with patch(
        COHERE_CLIENT_PATH,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        with pytest.raises(
            ValueError,
            match="query cannot be empty",
        ):
            provider.rerank(
                query="",
                documents=["Document one"],
            )


def test_whitespace_query_raises_error() -> None:
    """
    Verify that a whitespace-only query is rejected.
    """

    with patch(
        COHERE_CLIENT_PATH,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        with pytest.raises(
            ValueError,
            match="query cannot be empty",
        ):
            provider.rerank(
                query="   ",
                documents=["Document one"],
            )


def test_empty_documents_returns_empty_results() -> None:
    """
    Verify that an empty document collection returns no results.
    """

    with patch(
        COHERE_CLIENT_PATH,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        results = provider.rerank(
            query="test query",
            documents=[],
        )

        assert results == []


def test_invalid_top_k_raises_error() -> None:
    """
    Verify that top_k must be greater than zero.
    """

    with patch(
        COHERE_CLIENT_PATH,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        with pytest.raises(
            ValueError,
            match="top_k must be greater than zero",
        ):
            provider.rerank(
                query="test query",
                documents=["Document one"],
                top_k=0,
            )


def test_rerank_maps_cohere_results() -> None:
    """
    Verify that Cohere results are mapped to RerankResult.
    """

    mock_client = MagicMock()

    mock_client.rerank.return_value = create_mock_response(
        [
            (1, 0.95),
            (0, 0.72),
        ]
    )

    with patch(
        COHERE_CLIENT_PATH,
        return_value=mock_client,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        documents = [
            "Document one",
            "Document two",
        ]

        results = provider.rerank(
            query="test query",
            documents=documents,
        )

    assert results == [
        RerankResult(
            index=1,
            score=0.95,
        ),
        RerankResult(
            index=0,
            score=0.72,
        ),
    ]


def test_rerank_calls_cohere_with_expected_arguments() -> None:
    """
    Verify that the provider calls Cohere with the expected
    query, documents, model, and top_n.
    """

    mock_client = MagicMock()

    mock_client.rerank.return_value = create_mock_response(
        [
            (2, 0.91),
            (0, 0.74),
        ]
    )

    with patch(
        COHERE_CLIENT_PATH,
        return_value=mock_client,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
            model_name="rerank-v4.0-pro",
        )

        documents = [
            "Document one",
            "Document two",
            "Document three",
        ]

        provider.rerank(
            query="What is the leave policy?",
            documents=documents,
            top_k=2,
        )

    mock_client.rerank.assert_called_once_with(
        model="rerank-v4.0-pro",
        query="What is the leave policy?",
        documents=documents,
        top_n=2,
    )


def test_rerank_limits_top_k_to_document_count() -> None:
    """
    Verify that top_k larger than the document count is reduced
    to the number of available documents.
    """

    mock_client = MagicMock()

    mock_client.rerank.return_value = create_mock_response(
        [
            (0, 0.91),
            (1, 0.82),
        ]
    )

    with patch(
        COHERE_CLIENT_PATH,
        return_value=mock_client,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        documents = [
            "Document one",
            "Document two",
        ]

        provider.rerank(
            query="test query",
            documents=documents,
            top_k=10,
        )

    mock_client.rerank.assert_called_once_with(
        model="rerank-v4.0-fast",
        query="test query",
        documents=documents,
        top_n=2,
    )


def test_rerank_preserves_cohere_result_order() -> None:
    """
    Verify that the provider preserves Cohere's ranking order.
    """

    mock_client = MagicMock()

    mock_client.rerank.return_value = create_mock_response(
        [
            (3, 0.99),
            (1, 0.87),
            (0, 0.64),
        ]
    )

    with patch(
        COHERE_CLIENT_PATH,
        return_value=mock_client,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        results = provider.rerank(
            query="test query",
            documents=[
                "Document zero",
                "Document one",
                "Document two",
                "Document three",
            ],
        )

    assert [result.index for result in results] == [
        3,
        1,
        0,
    ]

    assert [result.score for result in results] == [
        0.99,
        0.87,
        0.64,
    ]


def test_close_does_not_raise_error() -> None:
    """
    Verify that the provider can be closed safely.
    """

    with patch(
        COHERE_CLIENT_PATH,
    ):
        provider = CohereRerankerProvider(
            api_key="test-api-key",
        )

        provider.close()
