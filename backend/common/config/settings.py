"""
backend/common/config/settings.py

Top-level application settings for the RAGOps platform.
"""

from __future__ import annotations

from pydantic import Field

from .base import (
    BaseConfig,
    FeatureFlags,
    HealthCheckConfig,
    PathConfig,
)
from .environment import Environment, get_environment
from .logging import LoggingConfig
from .providers import (
    EmbeddingProviderConfig,
    LLMProviderConfig,
    OCRProviderConfig,
    RerankerProviderConfig,
    SpeechProviderConfig,
    StorageProviderConfig,
    VectorStoreConfig,
)
from .security import (
    AuthenticationConfig,
    AuthorizationConfig,
    CORSConfig,
    EncryptionConfig,
)


class ApplicationSettings(BaseConfig):
    """Root application configuration."""

    application_name: str = "RAGOps Platform"
    version: str = "1.0.0"

    environment: Environment = Field(default_factory=get_environment)

    paths: PathConfig = Field(default_factory=PathConfig)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    health: HealthCheckConfig = Field(default_factory=HealthCheckConfig)

    logging: LoggingConfig

    authentication: AuthenticationConfig
    authorization: AuthorizationConfig = Field(default_factory=AuthorizationConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    encryption: EncryptionConfig = Field(default_factory=EncryptionConfig)

    llm: LLMProviderConfig
    embeddings: EmbeddingProviderConfig
    vector_store: VectorStoreConfig

    reranker: RerankerProviderConfig | None = None
    storage: StorageProviderConfig | None = None
    ocr: OCRProviderConfig | None = None
    speech: SpeechProviderConfig | None = None
    storage_root: str = "storage"


__all__ = [
    "ApplicationSettings",
]
