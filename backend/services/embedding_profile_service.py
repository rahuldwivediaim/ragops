
"""Embedding profile resolution and validation service."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.embeddings.providers.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from backend.models.embedding_profile import EmbeddingProfile
from backend.models.enums import EmbeddingProvider


class EmbeddingProfileService:
    """Resolve or create embedding profiles from application configuration."""

    def __init__(
        self,
        *,
        session: Session,
        embedding_provider: BaseEmbeddingProvider,
    ) -> None:
        self._session = session
        self._embedding_provider = embedding_provider

    def get_or_create(
        self,
        *,
        settings: Any,
    ) -> EmbeddingProfile:
        """Resolve an active compatible profile or create a new one."""

        provider = EmbeddingProvider(
            settings.embeddings.provider.value.upper(),
        )

        dimensions = settings.embeddings.dimensions

        if dimensions is None:
            dimensions = self._embedding_provider.dimensions

        if dimensions != self._embedding_provider.dimensions:
            raise ValueError(
                "Configured embedding dimensions do not match the active "
                f"embedding provider: configured={dimensions}, "
                f"provider={self._embedding_provider.dimensions}."
            )

        model_name = settings.embeddings.model
        name = f"{provider.value}-{model_name}-{dimensions}"

        statement = select(EmbeddingProfile).where(
            EmbeddingProfile.name == name,
        )

        profile = self._session.scalar(statement)

        if profile is not None:
            if not profile.is_active:
                raise ValueError(
                    f"Embedding profile '{name}' is inactive."
                )

            self._validate(
                profile=profile,
                provider=provider,
                model_name=model_name,
                dimensions=dimensions,
            )

            return profile

        profile = EmbeddingProfile(
            name=name,
            description=(
                "Application-configured embedding profile for "
                f"{provider.value} {model_name}."
            ),
            provider=provider,
            model_name=model_name,
            dimensions=dimensions,
            is_default=True,
            is_active=True,
        )

        self._session.add(profile)
        self._session.flush()

        return profile

    @staticmethod
    def _validate(
        *,
        profile: EmbeddingProfile,
        provider: EmbeddingProvider,
        model_name: str,
        dimensions: int,
    ) -> None:
        """Ensure the persisted profile matches runtime configuration."""

        if profile.provider != provider:
            raise ValueError(
                "Persisted embedding profile provider does not match "
                "application configuration."
            )

        if profile.model_name != model_name:
            raise ValueError(
                "Persisted embedding profile model does not match "
                "application configuration."
            )

        if profile.dimensions != dimensions:
            raise ValueError(
                "Persisted embedding profile dimensions do not match "
                "application configuration."
            )


__all__ = ["EmbeddingProfileService"]