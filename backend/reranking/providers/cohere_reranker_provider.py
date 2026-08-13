"""
Cohere reranker provider.

Provides reranking using Cohere's official Python SDK.
"""

from __future__ import annotations


import cohere

from backend.reranking.models import RerankResult
from backend.reranking.providers.base_reranker import (
    BaseReranker,
)


class CohereRerankerProvider(BaseReranker):
    """
    Reranker provider backed by Cohere.
    """

    DEFAULT_MODEL = "rerank-v4.0-fast"

    def __init__(
        self,
        api_key: str,
        model_name: str = DEFAULT_MODEL,
    ) -> None:
        if not api_key:
            raise ValueError("Cohere API key cannot be empty.")

        if not model_name:
            raise ValueError("Cohere reranker model name cannot be empty.")

        self._api_key = api_key
        self._model_name = model_name

        self._client = cohere.ClientV2(
            api_key=api_key,
        )

    @property
    def provider_name(self) -> str:
        """
        Return the reranker provider name.
        """

        return "cohere"

    @property
    def model_name(self) -> str:
        """
        Return the configured reranker model name.
        """

        return self._model_name

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[RerankResult]:
        """
        Rerank documents against a query using Cohere.

        Args:
            query: User search query.
            documents: Candidate documents to rerank.
            top_k: Maximum number of results to return.

        Returns:
            Reranked results using the framework-standard
            RerankResult model.
        """

        if not query or not query.strip():
            raise ValueError("query cannot be empty.")

        if not documents:
            return []

        if top_k is not None and top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if top_k is not None:
            top_k = min(
                top_k,
                len(documents),
            )

        response = self._client.rerank(
            model=self._model_name,
            query=query,
            documents=documents,
            top_n=top_k,
        )

        results: list[RerankResult] = []

        for result in response.results:
            results.append(
                RerankResult(
                    index=int(result.index),
                    score=float(result.relevance_score),
                )
            )

        return results

    def close(self) -> None:
        """
        Close the Cohere client.

        Cohere's client does not require explicit cleanup
        for the current synchronous usage pattern.
        """
        return None


__all__ = [
    "CohereRerankerProvider",
]
