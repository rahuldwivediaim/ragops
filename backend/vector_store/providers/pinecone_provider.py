"""
Pinecone Vector Store Provider.

Provides a managed vector store implementation using Pinecone.
"""

from __future__ import annotations

from typing import Any

from pinecone import Pinecone

from backend.vector_store.providers.base_vector_store import (
    BaseVectorStore,
)


class PineconeProvider(BaseVectorStore):
    """
    Vector store provider backed by Pinecone.
    """

    def __init__(
        self,
        api_key: str,
        index_name: str,
        namespace: str = "default",
    ) -> None:
        if not api_key:
            raise ValueError(
                "Pinecone API key cannot be empty."
            )

        if not index_name:
            raise ValueError(
                "Pinecone index name cannot be empty."
            )

        self._client = Pinecone(
            api_key=api_key,
        )

        self._index_name = index_name
        self._namespace = namespace

        self._index = self._client.Index(
            index_name,
        )

    @property
    def provider_name(
        self,
    ) -> str:
        """
        Return the vector store provider name.
        """

        return "pinecone"

    @property
    def index_name(
        self,
    ) -> str:
        """
        Return the Pinecone index name.
        """

        return self._index_name

    @property
    def namespace(
        self,
    ) -> str:
        """
        Return the Pinecone namespace.
        """

        return self._namespace

    def upsert(
        self,
        vector_id: str,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """
        Insert or update a vector in Pinecone.
        """

        if not vector_id:
            raise ValueError(
                "vector_id cannot be empty."
            )

        if not vector:
            raise ValueError(
                "vector cannot be empty."
            )

        self._index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": metadata,
                }
            ],
            namespace=self._namespace,
        )
    
    def upsert_batch(
        self,
        vectors: list[dict[str, Any]],
    ) -> None:
        """
        Insert or update multiple vectors in Pinecone in one request.

        Each vector must contain:
            - id
            - values
            - metadata
        """

        if not vectors:
            return

        for vector in vectors:
            vector_id = vector.get("id")
            values = vector.get("values")
            metadata = vector.get("metadata")

            if not vector_id:
                raise ValueError(
                    "Each vector must contain a non-empty 'id'."
                )

            if not values:
                raise ValueError(
                    f"Vector '{vector_id}' must contain non-empty 'values'."
                )

            if metadata is None:
                raise ValueError(
                    f"Vector '{vector_id}' must contain 'metadata'."
                )

        self._index.upsert(
            vectors=vectors,
            namespace=self._namespace,
        )

    def delete(
        self,
        vector_ids: list[str],
    ) -> None:
        """
        Delete vectors by their identifiers.
        """

        if not vector_ids:
            return

        self._index.delete(
            ids=vector_ids,
            namespace=self._namespace,
        )

    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search Pinecone for similar vectors.
        """

        if not vector:
            raise ValueError(
                "vector cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        response = self._index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            namespace=self._namespace,
            filter=metadata_filter,
        )

        results: list[dict[str, Any]] = []

        for match in response.matches:
            results.append(
                {
                    "vector_id": match.id,
                    "score": float(match.score),
                    "metadata": dict(
                        match.metadata or {}
                    ),
                }
            )

        return results

    def count(
        self,
    ) -> int:
        """
        Return the total number of vectors in the index.

        The count is retrieved from the selected namespace.
        """

        statistics = self._index.describe_index_stats()

        namespace_statistics = statistics.namespaces.get(
            self._namespace,
        )

        if namespace_statistics is None:
            return 0

        return int(
            namespace_statistics.vector_count
        )

    def close(
        self,
    ) -> None:
        """
        Close Pinecone HTTP resources.
        """

        self._index.close()
        self._client.close()


__all__ = [
    "PineconeProvider",
]