"""
backend/common/config/providers.py

Provider configuration models for external AI and infrastructure services.
"""

from __future__ import annotations

from pydantic import AnyHttpUrl, Field

from backend.common.enums import (
    EmbeddingProvider,
    LLMProvider,
    VectorStore,
)

from .base import BaseConfig, RetryPolicy


class ProviderConfig(BaseConfig):
    """Base provider configuration."""

    enabled: bool = True
    endpoint: AnyHttpUrl | None = None
    timeout_seconds: int = Field(default=60, ge=1)
    retry: RetryPolicy = Field(default_factory=RetryPolicy)


class LLMProviderConfig(ProviderConfig):
    provider: LLMProvider
    model: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)


class EmbeddingProviderConfig(ProviderConfig):
    provider: EmbeddingProvider
    model: str
    dimensions: int | None = None


class VectorStoreConfig(ProviderConfig):
    provider: VectorStore
    index_name: str
    namespace: str | None = None


class RerankerProviderConfig(ProviderConfig):
    provider: LLMProvider
    model: str


class OCRProviderConfig(ProviderConfig):
    provider: str
    language: str = "en"


class StorageProviderConfig(ProviderConfig):
    provider: str
    bucket: str | None = None
    container: str | None = None


class SpeechProviderConfig(ProviderConfig):
    provider: str
    model: str | None = None
    voice: str | None = None


__all__ = [
    "ProviderConfig",
    "LLMProviderConfig",
    "EmbeddingProviderConfig",
    "VectorStoreConfig",
    "RerankerProviderConfig",
    "OCRProviderConfig",
    "StorageProviderConfig",
    "SpeechProviderConfig",
]
