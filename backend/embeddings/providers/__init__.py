"""
Embedding providers.

This package contains all supported embedding providers.
"""

from .base_embedding_provider import BaseEmbeddingProvider
from .openai_embedding_provider import OpenAIEmbeddingProvider

__all__ = [
    "BaseEmbeddingProvider",
    "OpenAIEmbeddingProvider",
]