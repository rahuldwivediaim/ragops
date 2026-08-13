"""
Local Sentence Transformers CrossEncoder reranker provider.

Uses the official sentence-transformers library and a pretrained
CrossEncoder model for document reranking.
"""

from __future__ import annotations

from sentence_transformers import CrossEncoder

from backend.reranking.models import RerankResult
from backend.reranking.providers.base_reranker import (
    BaseReranker,
)


class SentenceTransformerRerankerProvider(BaseReranker):
    """
    Local reranker backed by a Sentence Transformers CrossEncoder.
    """

    DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str | None = None,
    ) -> None:
        if not model_name:
            raise ValueError(
                "Sentence Transformer reranker model name cannot be empty."
            )

        self._model_name = model_name

        model_kwargs: dict[str, str] = {}

        if device is not None:
            if not device:
                raise ValueError("device cannot be empty.")

            model_kwargs["device"] = device

        self._model = CrossEncoder(
            model_name,
            **model_kwargs,
        )

    @property
    def provider_name(self) -> str:
        """
        Return the reranker provider name.
        """

        return "sentence_transformers"

    @property
    def model_name(self) -> str:
        """
        Return the configured CrossEncoder model name.
        """

        return self._model_name

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[RerankResult]:
        """
        Rerank documents against a query using the local CrossEncoder.

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

        pairs = [[query, document] for document in documents]

        # The MS MARCO CrossEncoder returns one relevance score
        # per query/document pair. Do not apply softmax here.
        #
        # Applying softmax to a single score produces 1.0 and
        # destroys the relative relevance information needed
        # for reranking.
        scores = self._model.predict(
            pairs,
            apply_softmax=False,
        )

        results = [
            RerankResult(
                index=index,
                score=float(score),
            )
            for index, score in enumerate(scores)
        ]

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        if top_k is not None:
            return results[:top_k]

        return results

    def close(self) -> None:
        """
        Release local model resources.

        Sentence Transformers does not require an explicit
        close operation for the current CrossEncoder usage.
        """

        return None


__all__ = [
    "SentenceTransformerRerankerProvider",
]
