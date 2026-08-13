"""
Tests for authorization decisions.
"""

from backend.authorization.models.authorization_decision import (
    AuthorizationDecision,
    Decision,
)


def test_allow_decision() -> None:
    decision = AuthorizationDecision(
        decision=Decision.ALLOW,
        reason="User has the required permission.",
    )

    assert decision.decision is Decision.ALLOW
    assert decision.allowed is True


def test_deny_decision() -> None:
    decision = AuthorizationDecision(
        decision=Decision.DENY,
        reason="User does not have the required permission.",
    )

    assert decision.decision is Decision.DENY
    assert decision.allowed is False
