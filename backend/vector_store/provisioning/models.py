"""
Provider-neutral models for vector infrastructure provisioning.

These models describe infrastructure ownership and validation results without
coupling the setup workflow to a particular vector database.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.enums import VectorInfrastructureMode


@dataclass(frozen=True)
class VectorIndexSpec:
    """Desired physical vector-index characteristics."""

    index_name: str
    namespace: str
    dimensions: int
    metric: str = "cosine"
    cloud: str = "aws"
    region: str = "us-east-1"


@dataclass(frozen=True)
class VectorIndexInspection:
    """Observed state of a physical vector index."""

    exists: bool
    index_name: str
    dimension: int | None = None
    metric: str | None = None
    ready: bool = False
    host: str | None = None
    cloud: str | None = None
    region: str | None = None


@dataclass(frozen=True)
class VectorCompatibilityResult:
    """Result of validating an existing vector index."""

    compatible: bool
    messages: tuple[str, ...] = ()
    inspection: VectorIndexInspection | None = None

    @property
    def summary(self) -> str:
        """Return a concise operator-facing validation summary."""
        if self.compatible:
            return "Vector index is compatible with the requested configuration."

        if self.messages:
            return " ".join(self.messages)

        return "Vector index is not compatible."


__all__ = [
    "VectorCompatibilityResult",
    "VectorIndexInspection",
    "VectorIndexSpec",
    "VectorInfrastructureMode",
]