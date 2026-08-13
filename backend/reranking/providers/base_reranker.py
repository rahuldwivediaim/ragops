"""
Base interface for reranker providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.reranking.models import RerankResult


class BaseReranker(ABC):
    """
    Abstract interface for reranking providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the reranker provider name.
        """
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Return the reranker model name.
        """
        ...

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[RerankResult]:
        """
        Rerank documents against a query.

        Args:
            query: User search query.
            documents: Candidate documents to rerank.
            top_k: Maximum number of results to return.

        Returns:
            Reranked results using the framework-standard
            RerankResult model.
        """
        ...

    def close(self) -> None:
        """
        Release provider resources.

        Providers that do not require explicit cleanup may
        use the default implementation.
        """
        return None


__all__ = [
    "BaseReranker",
]
