"""
FAISS Vector Store Provider.

Provides a local vector store implementation using FAISS.

Cosine similarity is implemented using normalized vectors and
FAISS inner-product search.
"""

from __future__ import annotations

from typing import Any

import faiss
import numpy as np

from backend.vector_store.providers.base_vector_store import (
    BaseVectorStore,
)


class FAISSProvider(BaseVectorStore):
    """
    Local vector store backed by FAISS.

    The provider keeps vector metadata in memory alongside the
    FAISS index. This implementation is intended for local
    development and testing.
    """

    def __init__(
        self,
        dimensions: int | None = None,
    ) -> None:
        if dimensions is not None and dimensions <= 0:
            raise ValueError("dimensions must be greater than zero.")

        self._dimensions = dimensions
        self._index: faiss.Index | None = None

        self._vector_ids: list[str] = []
        self._metadata: dict[str, dict[str, Any]] = {}

    @property
    def provider_name(self) -> str:
        """
        Return the vector store provider name.
        """

        return "faiss"

    @property
    def dimensions(self) -> int | None:
        """
        Return the configured vector dimensions.
        """

        return self._dimensions

    def _ensure_index(
        self,
        dimensions: int,
    ) -> None:
        """
        Create the FAISS index if it does not already exist.
        """

        if dimensions <= 0:
            raise ValueError("Vector dimensions must be greater than zero.")

        if self._dimensions is None:
            self._dimensions = dimensions

        if dimensions != self._dimensions:
            raise ValueError(
                f"Vector dimensions {dimensions} do not match "
                f"configured dimensions {self._dimensions}."
            )

        if self._index is None:
            self._index = faiss.IndexFlatIP(
                self._dimensions,
            )

    def _validate_vector(
        self,
        vector: list[float],
    ) -> np.ndarray:
        """
        Validate and normalize a vector for cosine similarity.
        """

        if not vector:
            raise ValueError("Vector cannot be empty.")

        array = np.asarray(
            vector,
            dtype=np.float32,
        ).reshape(1, -1)

        self._ensure_index(
            array.shape[1],
        )

        faiss.normalize_L2(array)

        return array

    def upsert(
        self,
        vector_id: str,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """
        Insert or replace a vector.
        """

        if not vector_id:
            raise ValueError("vector_id cannot be empty.")

        if vector_id in self._vector_ids:
            self.delete([vector_id])

        normalized_vector = self._validate_vector(
            vector,
        )

        if self._index is None:
            raise RuntimeError("FAISS index has not been initialized.")

        self._index.add(normalized_vector)

        self._vector_ids.append(vector_id)

        self._metadata[vector_id] = dict(metadata)

    def delete(
        self,
        vector_ids: list[str],
    ) -> None:
        """
        Delete vectors by their identifiers.

        FAISS IndexFlatIP does not provide convenient deletion by
        external string identifiers, so the local index is rebuilt.
        """

        if not vector_ids:
            return

        ids_to_delete = set(vector_ids)

        remaining_ids = [
            vector_id
            for vector_id in self._vector_ids
            if vector_id not in ids_to_delete
        ]

        if len(remaining_ids) == len(self._vector_ids):
            return

        remaining_vectors: list[list[float]] = []

        if self._index is not None and self._vector_ids:
            stored_vectors = self._index.reconstruct_n(
                0,
                len(self._vector_ids),
            )

            for index, vector_id in enumerate(self._vector_ids):
                if vector_id not in ids_to_delete:
                    remaining_vectors.append(stored_vectors[index].tolist())

        self._vector_ids = remaining_ids

        for vector_id in ids_to_delete:
            self._metadata.pop(
                vector_id,
                None,
            )

        self._index = None

        if self._dimensions is not None:
            self._index = faiss.IndexFlatIP(
                self._dimensions,
            )

        if remaining_vectors:
            vectors = np.asarray(
                remaining_vectors,
                dtype=np.float32,
            )

            faiss.normalize_L2(vectors)

            if self._index is None:
                raise RuntimeError("FAISS index has not been initialized.")

            self._index.add(vectors)

    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for the most similar vectors.

        Results are ordered by descending cosine similarity.
        """

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if self._index is None or not self._vector_ids:
            return []

        query_vector = self._validate_vector(
            vector,
        )

        if self._index is None:
            raise RuntimeError("FAISS index has not been initialized.")

        limit = min(
            top_k,
            len(self._vector_ids),
        )

        scores, indexes = self._index.search(
            query_vector,
            limit,
        )

        results: list[dict[str, Any]] = []

        for score, index in zip(
            scores[0],
            indexes[0],
        ):
            if index < 0:
                continue

            vector_id = self._vector_ids[index]

            metadata = self._metadata.get(
                vector_id,
                {},
            )

            if metadata_filter and not self._matches_filter(
                metadata,
                metadata_filter,
            ):
                continue

            results.append(
                {
                    "vector_id": vector_id,
                    "score": float(score),
                    "metadata": dict(metadata),
                }
            )

        return results

    def _matches_filter(
        self,
        metadata: dict[str, Any],
        metadata_filter: dict[str, Any],
    ) -> bool:
        """
        Check whether metadata satisfies a simple equality filter.
        """

        return all(metadata.get(key) == value for key, value in metadata_filter.items())

    def count(self) -> int:
        """
        Return the number of stored vectors.
        """

        if self._index is None:
            return 0

        return self._index.ntotal


__all__ = [
    "FAISSProvider",
]
