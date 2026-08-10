"""
Base Vector Store Provider.

Defines the common contract implemented by all vector database
providers such as FAISS and Pinecone.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseVectorStore(ABC):
    """
    Base interface for vector store providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the vector store provider name.
        """

    @abstractmethod
    def upsert(
        self,
        vector_id: str,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """
        Insert or update a vector.
        """

    @abstractmethod
    def delete(
        self,
        vector_ids: list[str],
    ) -> None:
        """
        Delete vectors by their identifiers.
        """

    @abstractmethod
    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for similar vectors.
        """

    @abstractmethod
    def count(self) -> int:
        """
        Return the number of stored vectors.
        """


__all__ = [
    "BaseVectorStore",
]