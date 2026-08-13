"""
Authorization access-scope model.

Represents the effective domains and knowledge bases a user is
authorized to access.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AccessScope:
    """
    Effective authorization scope for a user.

    The scope is the union of the access policies associated
    with all roles assigned to the user.
    """

    domains: frozenset[str] = frozenset()
    knowledge_bases: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        """Validate the access-scope identifiers."""

        for domain_id in self.domains:
            if not domain_id.strip():
                raise ValueError(
                    "Access scope domain id cannot be empty.",
                )

        for knowledge_base_id in self.knowledge_bases:
            if not knowledge_base_id.strip():
                raise ValueError(
                    "Access scope knowledge-base id cannot be empty.",
                )

    def includes_domain(self, domain_id: str) -> bool:
        """Return whether the scope includes the specified domain."""

        return domain_id in self.domains

    def includes_knowledge_base(
        self,
        knowledge_base_id: str,
    ) -> bool:
        """
        Return whether the scope includes the specified
        knowledge base.
        """

        return knowledge_base_id in self.knowledge_bases

    def union(self, other: AccessScope) -> AccessScope:
        """Return the union of this scope and another scope."""

        return AccessScope(
            domains=self.domains | other.domains,
            knowledge_bases=(self.knowledge_bases | other.knowledge_bases),
        )


__all__ = ["AccessScope"]
