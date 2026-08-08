"""
Base Embedding Provider.

Defines the contract implemented by every embedding provider.

Examples:
    - OpenAI
    - Azure OpenAI
    - Voyage AI
    - Cohere
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


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
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Default batch implementation.
        """

        return [self.embed(text) for text in texts]


__all__ = [
    "BaseEmbeddingProvider",
]
