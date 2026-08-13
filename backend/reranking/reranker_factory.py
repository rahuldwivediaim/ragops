"""
Factory for creating reranker providers.

The factory is responsible only for selecting and creating
the configured reranker provider.
"""

from __future__ import annotations

from backend.reranking.providers.base_reranker import (
    BaseReranker,
)
from backend.reranking.providers.cohere_reranker_provider import (
    CohereRerankerProvider,
)
from backend.reranking.providers.sentence_transformer_reranker_provider import (
    SentenceTransformerRerankerProvider,
)


class RerankerFactory:
    """
    Factory for creating reranker provider instances.
    """

    @staticmethod
    def create(
        provider: str,
        api_key: str | None = None,
        model_name: str | None = None,
        device: str | None = None,
    ) -> BaseReranker:
        """
        Create a reranker provider.

        Args:
            provider: Reranker provider name.
            api_key: Provider API key for hosted providers.
            model_name: Optional provider model name.
            device: Optional execution device for local providers.

        Returns:
            Configured reranker provider.

        Raises:
            ValueError:
                If the provider is unsupported or required
                configuration is missing.
        """

        provider_name = provider.strip().lower()

        if provider_name == "cohere":
            if not api_key:
                raise ValueError("Cohere API key is required.")

            if model_name is None:
                return CohereRerankerProvider(
                    api_key=api_key,
                )

            return CohereRerankerProvider(
                api_key=api_key,
                model_name=model_name,
            )

        if provider_name in {
            "sentence_transformers",
            "sentence-transformers",
            "cross_encoder",
            "cross-encoder",
        }:
            if model_name is None:
                return SentenceTransformerRerankerProvider(
                    device=device,
                )

            return SentenceTransformerRerankerProvider(
                model_name=model_name,
                device=device,
            )

        raise ValueError(f"Unsupported reranker provider: {provider}")


__all__ = [
    "RerankerFactory",
]
