"""
Base Embedding Provider.

Defines the contract implemented by every embedding provider.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.embeddings.models.embedding_result import (
    EmbeddingResult,
)


class BaseEmbeddingProvider(ABC):
    """
    Base class for embedding providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Provider name.
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Embedding model name.
        """

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """
        Embedding dimensions.
        """

    @abstractmethod
    def embed(
        self,
        text: str,
    ) -> EmbeddingResult:
        """
        Generate an embedding.
        """

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.
        """

        return [self.embed(text) for text in texts]


__all__ = [
    "BaseEmbeddingProvider",
]
