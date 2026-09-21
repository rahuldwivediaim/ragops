"""
FastAPI dependencies for vector infrastructure setup.

This module builds the dependency graph required to configure vector
infrastructure through the API.

The infrastructure provider is responsible for physical vector-index
operations such as:

- inspecting an existing index
- validating an existing index
- creating a RAGOps-managed index

It does not perform vector writes or queries.
"""

from __future__ import annotations

import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.common.config.loader import load_settings
from backend.database.session import get_db
from backend.services.vector_infrastructure_setup_service import (
    VectorInfrastructureSetupService,
)
from backend.vector_store.provisioning.base import (
    BaseVectorInfrastructureProvider,
)
from backend.vector_store.provisioning.pinecone import (
    PineconeInfrastructureProvider,
)

load_dotenv()


def _build_infrastructure_provider(
    settings,
) -> BaseVectorInfrastructureProvider:
    """
    Build the configured vector infrastructure provider.

    The current implementation supports Pinecone.
    """

    if not settings.vector_store.enabled:
        raise RuntimeError(
            "Vector store is disabled in application configuration."
        )

    provider = settings.vector_store.provider.value

    if provider != "pinecone":
        raise RuntimeError(
            "Vector infrastructure setup currently supports only "
            f"Pinecone. Configured provider: {provider!r}."
        )

    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "PINECONE_API_KEY is not configured."
        )

    return PineconeInfrastructureProvider(
        api_key=api_key,
    )


def get_vector_infrastructure_service(
    session: Annotated[Session, Depends(get_db)],
) -> VectorInfrastructureSetupService:
    """
    Build the VectorInfrastructureSetupService dependency.
    """

    settings = load_settings()

    infrastructure_provider = _build_infrastructure_provider(
        settings,
    )

    return VectorInfrastructureSetupService(
        session=session,
        infrastructure_provider=infrastructure_provider,
    )


VectorInfrastructureServiceDependency = Annotated[
    VectorInfrastructureSetupService,
    Depends(get_vector_infrastructure_service),
]


__all__ = [
    "VectorInfrastructureServiceDependency",
    "get_vector_infrastructure_service",
]