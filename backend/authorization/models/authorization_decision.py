"""
Authorization decision model.

Represents the result produced by an authorization service.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Decision(StrEnum):
    """Possible authorization outcomes."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """
    Result of an authorization evaluation.
    """

    decision: Decision
    reason: str

    @property
    def allowed(self) -> bool:
        """Return whether access was granted."""

        return self.decision is Decision.ALLOW


__all__ = [
    "AuthorizationDecision",
    "Decision",
]
