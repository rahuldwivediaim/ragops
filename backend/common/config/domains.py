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
    """

    name: str
    description: str
    enabled: bool = True

    def __init__(self, **data: object) -> None:
        super().__init__(**data)

        if not self.name.strip():
            raise ValueError("Domain name cannot be empty.")

        if not self.description.strip():
            raise ValueError("Domain description cannot be empty.")


__all__ = ["DomainConfig"]
