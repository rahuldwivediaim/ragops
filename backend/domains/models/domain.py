"""
Domain model.

Represents a logical business/domain boundary within RAGFramework.

A domain is intentionally independent of:
- vector stores
- embedding providers
- rerankers
- AI agents
- authorization

Those concerns consume the domain contract later.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Domain:
    """
    Represents a configurable RAG domain.

    Domains may form a hierarchy.

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

    parent_id
        Identifier of the parent domain. None indicates a root
        domain.
    """

    id: str
    name: str
    description: str
    enabled: bool = True
    parent_id: str | None = None

    def __post_init__(self) -> None:
        """Validate the domain definition."""

        if not self.id.strip():
            raise ValueError("Domain id cannot be empty.")

        if not self.name.strip():
            raise ValueError("Domain name cannot be empty.")

        if not self.description.strip():
            raise ValueError("Domain description cannot be empty.")

        if self.parent_id is not None and not self.parent_id.strip():
            raise ValueError("Domain parent_id cannot be empty.")

        if self.parent_id == self.id:
            raise ValueError(
                f"Domain '{self.id}' cannot be its own parent.",
            )

    @property
    def is_root(self) -> bool:
        """Return whether this domain is a root domain."""

        return self.parent_id is None


__all__ = ["Domain"]
