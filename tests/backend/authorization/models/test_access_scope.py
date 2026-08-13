"""
Tests for the AccessScope model.
"""

import pytest

from backend.authorization.models.access_scope import AccessScope


def test_access_scope_creation() -> None:
    scope = AccessScope(
        domains=frozenset(
            {
                "employee_policies",
                "finance_policies",
            },
        ),
        knowledge_bases=frozenset(
            {
                "employee_kb",
                "finance_kb",
            },
        ),
    )

    assert scope.domains == frozenset(
        {
            "employee_policies",
            "finance_policies",
        },
    )

    assert scope.knowledge_bases == frozenset(
        {
            "employee_kb",
            "finance_kb",
        },
    )


def test_empty_access_scope() -> None:
    scope = AccessScope()

    assert scope.domains == frozenset()
    assert scope.knowledge_bases == frozenset()


def test_access_scope_can_check_domain() -> None:
    scope = AccessScope(
        domains=frozenset({"employee_policies"}),
    )

    assert scope.includes_domain("employee_policies") is True
    assert scope.includes_domain("finance_policies") is False


def test_access_scope_can_check_knowledge_base() -> None:
    scope = AccessScope(
        knowledge_bases=frozenset({"employee_kb"}),
    )

    assert scope.includes_knowledge_base("employee_kb") is True
    assert scope.includes_knowledge_base("finance_kb") is False


def test_access_scope_union() -> None:
    employee_scope = AccessScope(
        domains=frozenset({"employee_policies"}),
        knowledge_bases=frozenset({"employee_kb"}),
    )

    finance_scope = AccessScope(
        domains=frozenset({"finance_policies"}),
        knowledge_bases=frozenset({"finance_kb"}),
    )

    effective_scope = employee_scope.union(
        finance_scope,
    )

    assert effective_scope.domains == frozenset(
        {
            "employee_policies",
            "finance_policies",
        },
    )

    assert effective_scope.knowledge_bases == frozenset(
        {
            "employee_kb",
            "finance_kb",
        },
    )


@pytest.mark.parametrize(
    "domain_id",
    ["", "   "],
)
def test_access_scope_rejects_empty_domain(
    domain_id: str,
) -> None:
    with pytest.raises(ValueError):
        AccessScope(
            domains=frozenset({domain_id}),
        )


@pytest.mark.parametrize(
    "knowledge_base_id",
    ["", "   "],
)
def test_access_scope_rejects_empty_knowledge_base(
    knowledge_base_id: str,
) -> None:
    with pytest.raises(ValueError):
        AccessScope(
            knowledge_bases=frozenset(
                {knowledge_base_id},
            ),
        )
