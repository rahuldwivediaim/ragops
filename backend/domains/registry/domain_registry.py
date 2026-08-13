"""
Domain registry.

Maintains the domains available to RAGFramework.

The registry is intentionally independent of:
- AI agents
- retrieval
- vector stores
- authorization

Those components can consume the registry without knowing
how domains are stored or registered.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict

from backend.domains.models.domain import Domain


class DomainDefinition(TypedDict, total=False):
    """
    Runtime-compatible definition used to construct domains.
    """

    name: str
    description: str
    enabled: bool


class DomainRegistry:
    """
    Registry of available RAG domains.
    """

    def __init__(self, domains: list[Domain] | None = None) -> None:
        """
        Initialize the registry.

        Parameters
        ----------
        domains
            Optional initial collection of domains.
        """

        self._domains: dict[str, Domain] = {}

        for domain in domains or []:
            self.register(domain)

    @classmethod
    def from_definitions(
        cls,
        definitions: Mapping[str, DomainDefinition],
    ) -> "DomainRegistry":
        """
        Build a registry from domain definitions.

        Parameters
        ----------
        definitions
            Mapping of stable domain IDs to domain definitions.

        Returns
        -------
        DomainRegistry
            Registry containing the configured domains.
        """

        domains = [
            Domain(
                id=domain_id,
                name=definition["name"],
                description=definition["description"],
                enabled=definition.get("enabled", True),
            )
            for domain_id, definition in definitions.items()
        ]

        return cls(domains=domains)

    def register(self, domain: Domain) -> None:
        """
        Register a domain.

        Raises
        ------
        ValueError
            If a domain with the same ID is already registered.
        """

        if domain.id in self._domains:
            raise ValueError(f"Domain '{domain.id}' is already registered.")

        self._domains[domain.id] = domain

    def get(self, domain_id: str) -> Domain:
        """
        Return a domain by ID.

        Raises
        ------
        KeyError
            If the domain does not exist.
        """

        try:
            return self._domains[domain_id]
        except KeyError as exc:
            raise KeyError(f"Domain '{domain_id}' is not registered.") from exc

    def exists(self, domain_id: str) -> bool:
        """
        Return whether a domain is registered.
        """

        return domain_id in self._domains

    def list_all(self) -> list[Domain]:
        """
        Return all registered domains.
        """

        return list(self._domains.values())

    def list_enabled(self) -> list[Domain]:
        """
        Return all currently enabled domains.
        """

        return [domain for domain in self._domains.values() if domain.enabled]


__all__ = [
    "DomainDefinition",
    "DomainRegistry",
]
