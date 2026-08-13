"""
Retriever.

Coordinates query embedding generation, vector-store search,
and optional document reranking.
"""

from __future__ import annotations

from typing import Any

from backend.embeddings.providers.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from backend.reranking.providers.base_reranker import (
    BaseReranker,
)
from backend.vector_store.providers.base_vector_store import (
    BaseVectorStore,
)


class Retriever:
    """
    Retrieves the most relevant vectors for a text query.

    Retrieval is performed in two optional stages:

    1. Vector retrieval using the configured vector store.
    2. Reranking of retrieved candidates using an optional reranker.

    When no reranker is configured, the original vector-store
    ranking is preserved.
    """

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
        reranker: BaseReranker | None = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._reranker = reranker

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve and optionally rerank documents.

        Parameters
        ----------
        query:
            User's search query.

        top_k:
            Maximum number of results to return.

        metadata_filter:
            Optional vector-store metadata filter.

        Returns
        -------
        list[dict[str, Any]]
            Retrieved results, optionally reordered by the
            configured reranker.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        embedding_result = self._embedding_provider.embed(
            query,
        )

        results = self._vector_store.query(
            vector=embedding_result.vector,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

        if not results:
            return []

        reranker = self._reranker

        if reranker is None:
            return results

        return self._rerank_results(
            query=query,
            results=results,
            top_k=top_k,
            reranker=reranker,
        )

    def _rerank_results(
        self,
        query: str,
        results: list[dict[str, Any]],
        top_k: int,
        reranker: BaseReranker,
    ) -> list[dict[str, Any]]:
        """
        Rerank vector-store results using document text metadata.
        """

        documents: list[str] = []

        for index, result in enumerate(results):
            metadata = result.get("metadata")

            if not isinstance(metadata, dict):
                raise ValueError(
                    "Retrieved result at index "
                    f"{index} does not contain valid metadata."
                )

            text = metadata.get("text")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    "Retrieved result at index "
                    f"{index} does not contain valid text metadata."
                )

            documents.append(text)

        reranked_results = reranker.rerank(
            query=query,
            documents=documents,
            top_k=top_k,
        )

        return [results[result.index] for result in reranked_results]


__all__ = [
    "Retriever",
]
