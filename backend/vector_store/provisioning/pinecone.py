"""
Pinecone infrastructure provisioning and compatibility validation.

This component is intentionally separate from PineconeProvider. Constructing
the operational PineconeProvider still assumes that the physical index
already exists; this class is responsible for checking or creating that
infrastructure before the operational provider is constructed.
"""

from __future__ import annotations

from typing import Any

from pinecone import Pinecone, ServerlessSpec

from backend.vector_store.provisioning.base import (
    BaseVectorInfrastructureProvider,
)
from backend.vector_store.provisioning.models import (
    VectorCompatibilityResult,
    VectorIndexInspection,
    VectorIndexSpec,
)


def _read_value(value: Any, key: str) -> Any:
    """Read a value from SDK objects and dict-like responses."""
    if value is None:
        return None

    if isinstance(value, dict):
        return value.get(key)

    return getattr(value, key, None)


class PineconeInfrastructureProvider(BaseVectorInfrastructureProvider):
    """Manage Pinecone index infrastructure without writing vectors."""

    def __init__(
        self,
        *,
        api_key: str,
    ) -> None:
        if not api_key:
            raise ValueError("Pinecone API key cannot be empty.")

        self._client = Pinecone(api_key=api_key)

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "pinecone"

    def inspect_index(
        self,
        *,
        index_name: str,
    ) -> VectorIndexInspection:
        """Inspect an index without creating or modifying it."""
        if not index_name:
            raise ValueError("index_name cannot be empty.")

        indexes = self._client.list_indexes()
        names = self._index_names(indexes)

        if index_name not in names:
            return VectorIndexInspection(
                exists=False,
                index_name=index_name,
            )

        description = self._client.describe_index(index_name)

        status = _read_value(description, "status")
        if status is None:
            status = {}

        return VectorIndexInspection(
            exists=True,
            index_name=index_name,
            dimension=_read_value(description, "dimension"),
            metric=_read_value(description, "metric"),
            ready=_read_value(status, "ready") is True,
            host=_read_value(description, "host"),
            cloud=_read_value(
                _read_value(description, "spec"),
                "cloud",
            ),
            region=_read_value(
                _read_value(description, "spec"),
                "region",
            ),
        )

    def validate_existing_index(
        self,
        *,
        spec: VectorIndexSpec,
    ) -> VectorCompatibilityResult:
        """
        Validate an existing customer-managed index.

        This method never creates an index and never writes or deletes vectors.
        """
        inspection = self.inspect_index(
            index_name=spec.index_name,
        )

        if not inspection.exists:
            return VectorCompatibilityResult(
                compatible=False,
                messages=(
                    f"Pinecone index {spec.index_name!r} does not exist.",
                ),
                inspection=inspection,
            )

        messages: list[str] = []

        if not inspection.ready:
            messages.append(
                f"Pinecone index {spec.index_name!r} is not ready."
            )

        if inspection.dimension != spec.dimensions:
            messages.append(
                "Embedding dimension mismatch: "
                f"index={inspection.dimension}, requested={spec.dimensions}."
            )

        if inspection.metric is not None:
            if inspection.metric.lower() != spec.metric.lower():
                messages.append(
                    "Vector metric mismatch: "
                    f"index={inspection.metric!r}, requested={spec.metric!r}."
                )

        compatible = not messages

        return VectorCompatibilityResult(
            compatible=compatible,
            messages=tuple(messages),
            inspection=inspection,
        )

    def ensure_index(
        self,
        *,
        spec: VectorIndexSpec,
    ) -> VectorIndexInspection:
        """
        Ensure a RAGOps-managed index exists.

        If the index exists, its compatibility is validated. If it does not
        exist, RAGOps creates it using the requested dimension/metric and
        serverless placement.
        """
        existing = self.inspect_index(
            index_name=spec.index_name,
        )

        if existing.exists:
            result = self.validate_existing_index(
                spec=spec,
            )
            if not result.compatible:
                raise ValueError(result.summary)

            return existing

        self._client.create_index(
            name=spec.index_name,
            dimension=spec.dimensions,
            metric=spec.metric,
            spec=ServerlessSpec(
                cloud=spec.cloud,
                region=spec.region,
            ),
        )

        created = self.inspect_index(
            index_name=spec.index_name,
        )

        if not created.exists:
            raise RuntimeError(
                f"Pinecone index {spec.index_name!r} was requested for creation "
                "but could not be found afterward."
            )

        return created

    def close(self) -> None:
        """Close the Pinecone control-plane client."""
        self._client.close()

    @staticmethod
    def _index_names(indexes: Any) -> set[str]:
        """Extract index names across Pinecone SDK response variants."""
        if hasattr(indexes, "names"):
            names = indexes.names()
            return set(names)

        if isinstance(indexes, (list, tuple)):
            return {
                str(_read_value(item, "name"))
                for item in indexes
                if _read_value(item, "name")
            }

        return {
            str(_read_value(item, "name"))
            for item in indexes
            if _read_value(item, "name")
        }


__all__ = [
    "PineconeInfrastructureProvider",
]
