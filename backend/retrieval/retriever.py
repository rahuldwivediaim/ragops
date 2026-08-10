"""
Retriever.

Coordinates query embedding generation and vector-store search.
"""

from __future__ import annotations

from typing import Any

from backend.embeddings.providers.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from backend.vector_store.providers.base_vector_store import (
    BaseVectorStore,
)


class Retriever:
    """
    Retrieves the most relevant vectors for a text query.
    """

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Convert a text query into an embedding and search the
        configured vector store.
        """

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        embedding_result = self._embedding_provider.embed(
            query,
        )

        return self._vector_store.query(
            vector=embedding_result.vector,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )


__all__ = [
    "Retriever",
]