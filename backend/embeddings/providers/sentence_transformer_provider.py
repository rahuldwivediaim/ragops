"""
Sentence Transformer Embedding Provider.

Generates embeddings using a local Hugging Face
Sentence Transformer model.
"""

from __future__ import annotations

import os

from sentence_transformers import SentenceTransformer

from backend.embeddings.models.embedding_result import (
    EmbeddingResult,
)
from backend.embeddings.providers.base_embedding_provider import (
    BaseEmbeddingProvider,
)


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """
    Local embedding provider using Sentence Transformers.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:

        # Prevent Windows symlink warning from Hugging Face.
        os.environ.setdefault(
            "HF_HUB_DISABLE_SYMLINKS_WARNING",
            "1",
        )

        self._model_name = model_name

        self._model = SentenceTransformer(
            model_name,
        )

    @property
    def provider_name(
        self,
    ) -> str:
        return "sentence-transformers"

    @property
    def model_name(
        self,
    ) -> str:
        return self._model_name

    @property
    def dimensions(
        self,
    ) -> int:
        return self._model.get_embedding_dimension()

    def embed(
        self,
        text: str,
    ) -> EmbeddingResult:
        """
        Generate an embedding for the supplied text.
        """

        vector = self._model.encode(
            text,
            convert_to_numpy=True,
        ).tolist()

        return EmbeddingResult(
            vector=vector,
            provider=self.provider_name,
            model_name=self.model_name,
            dimensions=self.dimensions,
            embedding_version=1,
        )


__all__ = [
    "SentenceTransformerProvider",
]