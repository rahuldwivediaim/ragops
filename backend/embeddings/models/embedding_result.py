"""
Embedding Result Model.

Represents the output produced by an embedding provider.

The result contains the embedding vector together with the metadata
required by downstream components such as vector stores and auditing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EmbeddingResult:
    """
    Result returned by an embedding provider.
    """

    vector: list[float]

    provider: str

    model_name: str

    dimensions: int

    embedding_version: int = 1

    @property
    def vector_length(
        self,
    ) -> int:
        """
        Length of the embedding vector.
        """

        return len(self.vector)

    def __repr__(
        self,
    ) -> str:
        return (
            "EmbeddingResult("
            f"provider='{self.provider}', "
            f"model='{self.model_name}', "
            f"dimensions={self.dimensions}, "
            f"vector_length={self.vector_length})"
        )


__all__ = [
    "EmbeddingResult",
]