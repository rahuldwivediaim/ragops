"""
Domain configuration models.

Defines configuration for the logical domains available to
RAGFramework.
"""

from __future__ import annotations

from .base import BaseConfig


class DomainConfig(BaseConfig):
    """
    Configuration for a single RAG domain.

    The dictionary key used under ApplicationSettings.domains
    is the stable domain identifier.

    Domains may form a hierarchy through parent_id.

    A root domain has parent_id=None.
    """

    name: str
    description: str
    enabled: bool = True
    parent_id: str | None = None

    def __init__(self, **data: object) -> None:
        super().__init__(**data)

        if not self.name.strip():
            raise ValueError("Domain name cannot be empty.")

        if not self.description.strip():
            raise ValueError("Domain description cannot be empty.")

        if self.parent_id is not None and not self.parent_id.strip():
            raise ValueError("Domain parent_id cannot be empty.")

    @property
    def is_root(self) -> bool:
        """Return whether this domain is a root domain."""

        return self.parent_id is None


__all__ = ["DomainConfig"]
