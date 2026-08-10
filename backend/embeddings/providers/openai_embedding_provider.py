"""
OpenAI Embedding Provider.

Generates embeddings using the OpenAI Embeddings API.
"""

from __future__ import annotations

from typing import Literal, cast

from openai import OpenAI

from backend.embeddings.models.embedding_result import (
    EmbeddingResult,
)
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
        dimensions: int | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key cannot be empty.")

        self._client = OpenAI(
            api_key=api_key,
        )

        self._model_name = model_name
        self._dimensions = dimensions

    @property
    def provider_name(
        self,
    ) -> str:
        """
        Return the embedding provider name.
        """

        return "openai"

    @property
    def model_name(
        self,
    ) -> str:
        """
        Return the embedding model name.
        """

        return self._model_name

    @property
    def dimensions(
        self,
    ) -> int:
        """
        Return the configured embedding dimensions.

        If dimensions were explicitly configured, return that
        value. Otherwise return the default dimension for the
        selected OpenAI embedding model.
        """

        if self._dimensions is not None:
            return self._dimensions

        if self._model_name == "text-embedding-3-large":
            return 3072

        return 1536

    def embed(
        self,
        text: str,
    ) -> EmbeddingResult:
        """
        Generate an embedding for a single text.
        """

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        model = cast(
            Literal[
                "text-embedding-ada-002",
                "text-embedding-3-small",
                "text-embedding-3-large",
            ],
            self._model_name,
        )

        if self._dimensions is None:
            response = self._client.embeddings.create(
                model=model,
                input=text,
            )
        else:
            response = self._client.embeddings.create(
                model=model,
                input=text,
                dimensions=self._dimensions,
            )

        vector = response.data[0].embedding

        return EmbeddingResult(
            vector=vector,
            provider=self.provider_name,
            model_name=self.model_name,
            dimensions=len(vector),
            embedding_version=1,
        )

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts in one
        OpenAI Embeddings API request.
        """

        if not texts:
            return []

        for index, text in enumerate(texts):
            if not text or not text.strip():
                raise ValueError(f"Text at index {index} cannot be empty.")

        model = cast(
            Literal[
                "text-embedding-ada-002",
                "text-embedding-3-small",
                "text-embedding-3-large",
            ],
            self._model_name,
        )

        if self._dimensions is None:
            response = self._client.embeddings.create(
                model=model,
                input=texts,
            )
        else:
            response = self._client.embeddings.create(
                model=model,
                input=texts,
                dimensions=self._dimensions,
            )

        # OpenAI returns an index for each embedding.
        # Sort explicitly so the result order always matches
        # the input text order.
        data = sorted(
            response.data,
            key=lambda item: item.index,
        )

        if len(data) != len(texts):
            raise RuntimeError(
                "OpenAI returned a different number of "
                "embeddings than the number of input texts."
            )

        results: list[EmbeddingResult] = []

        for item in data:
            vector = item.embedding

            results.append(
                EmbeddingResult(
                    vector=vector,
                    provider=self.provider_name,
                    model_name=self.model_name,
                    dimensions=len(vector),
                    embedding_version=1,
                )
            )

        return results

    def close(self) -> None:
        """
        Close the underlying OpenAI HTTP client.
        """

        self._client.close()


__all__ = [
    "OpenAIEmbeddingProvider",
]
