"""
Domain model.

Represents a logical business/domain boundary within RAGFramework.

A domain is intentionally independent of:
- vector stores
- embedding providers
- rerankers
- AI agents
- authorization

Those concerns will consume the domain contract later.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Domain:
    """
    Represents a configurable RAG domain.

    Parameters
    ----------
    id
        Stable unique identifier for the domain.

    name
        Human-readable domain name.

    description
        Semantic description used by the query-routing layer
        to understand what the domain contains.

    enabled
        Whether the domain is currently available for use.
    """

    id: str
    name: str
    description: str
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate the domain definition."""

        if not self.id.strip():
            raise ValueError("Domain id cannot be empty.")

        if not self.name.strip():
            raise ValueError("Domain name cannot be empty.")

        if not self.description.strip():
            raise ValueError("Domain description cannot be empty.")


__all__ = ["Domain"]
