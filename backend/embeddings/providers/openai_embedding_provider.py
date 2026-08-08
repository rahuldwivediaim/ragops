"""
OpenAI Embedding Provider.

Generates embeddings using the OpenAI Embeddings API.
"""

from __future__ import annotations

from openai import OpenAI

from backend.embeddings.providers.base_embedding_provider import (
    BaseEmbeddingProvider,
)


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    OpenAI embedding provider.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "text-embedding-3-small",
    ) -> None:
        self._client = OpenAI(
            api_key=api_key,
        )

        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        """
        Default dimensions for supported OpenAI models.

        If custom dimensions are requested in future,
        this property can be updated accordingly.
        """

        if self._model_name == "text-embedding-3-large":
            return 3072

        return 1536

    def embed(
        self,
        text: str,
    ) -> list[float]:
        response = self._client.embeddings.create(
            model=self._model_name,
            input=text,
        )

        return response.data[0].embedding


__all__ = [
    "OpenAIEmbeddingProvider",
]
