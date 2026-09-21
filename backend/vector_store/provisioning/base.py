"""
Provider-neutral vector infrastructure provisioning contract.

Operational vector stores remain responsible for upsert/query/delete.
Provisioners are responsible for infrastructure lifecycle and compatibility
validation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.vector_store.provisioning.models import (
    VectorCompatibilityResult,
    VectorIndexInspection,
    VectorIndexSpec,
)


class BaseVectorInfrastructureProvider(ABC):
    """Contract for vector infrastructure management."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier."""

    @abstractmethod
    def inspect_index(
        self,
        *,
        index_name: str,
    ) -> VectorIndexInspection:
        """Inspect an existing physical index without mutating it."""

    @abstractmethod
    def validate_existing_index(
        self,
        *,
        spec: VectorIndexSpec,
    ) -> VectorCompatibilityResult:
        """Validate an existing index against the desired configuration."""

    @abstractmethod
    def ensure_index(
        self,
        *,
        spec: VectorIndexSpec,
    ) -> VectorIndexInspection:
        """Create a missing index or validate an existing one."""

    @abstractmethod
    def close(self) -> None:
        """Release provider resources."""


__all__ = [
    "BaseVectorInfrastructureProvider",
]
