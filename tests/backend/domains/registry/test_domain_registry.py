"""
Tests for the DomainRegistry.
"""

import pytest

from backend.domains.models.domain import Domain
from backend.domains.registry.domain_registry import DomainRegistry


@pytest.fixture
def employee_domain() -> Domain:
    return Domain(
        id="employee_policies",
        name="Employee Policies",
        description=("Employee HR policies including leave, attendance and benefits."),
    )


@pytest.fixture
def finance_domain() -> Domain:
    return Domain(
        id="finance_policies",
        name="Finance Policies",
        description=(
            "Finance policies including expenses, reimbursements and approvals."
        ),
    )


def test_registry_can_register_domain(
    employee_domain: Domain,
) -> None:
    registry = DomainRegistry()

    registry.register(employee_domain)

    assert registry.exists("employee_policies")
    assert registry.get("employee_policies") == employee_domain


def test_registry_can_initialize_with_domains(
    employee_domain: Domain,
    finance_domain: Domain,
) -> None:
    registry = DomainRegistry(
        domains=[
            employee_domain,
            finance_domain,
        ]
    )

    assert registry.get("employee_policies") == employee_domain
    assert registry.get("finance_policies") == finance_domain


def test_registry_rejects_duplicate_domain(
    employee_domain: Domain,
) -> None:
    registry = DomainRegistry()

    registry.register(employee_domain)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(employee_domain)


def test_registry_rejects_unknown_domain() -> None:
    registry = DomainRegistry()

    with pytest.raises(
        KeyError,
        match="Domain 'unknown' is not registered",
    ):
        registry.get("unknown")


def test_registry_exists_returns_false_for_unknown_domain() -> None:
    registry = DomainRegistry()

    assert registry.exists("unknown") is False


def test_registry_lists_all_domains(
    employee_domain: Domain,
    finance_domain: Domain,
) -> None:
    registry = DomainRegistry(
        domains=[
            employee_domain,
            finance_domain,
        ]
    )

    domains = registry.list_all()

    assert domains == [
        employee_domain,
        finance_domain,
    ]


def test_registry_lists_only_enabled_domains(
    employee_domain: Domain,
    finance_domain: Domain,
) -> None:
    disabled_finance_domain = Domain(
        id=finance_domain.id,
        name=finance_domain.name,
        description=finance_domain.description,
        enabled=False,
    )

    registry = DomainRegistry(
        domains=[
            employee_domain,
            disabled_finance_domain,
        ]
    )

    assert registry.list_enabled() == [employee_domain]


def test_registry_can_be_created_from_definitions() -> None:
    registry = DomainRegistry.from_definitions(
        {
            "employee_policies": {
                "name": "Employee Policies",
                "description": "Employee HR policies.",
                "enabled": True,
            },
            "finance_policies": {
                "name": "Finance Policies",
                "description": "Finance policies.",
                "enabled": False,
            },
        }
    )

    assert registry.get("employee_policies") == Domain(
        id="employee_policies",
        name="Employee Policies",
        description="Employee HR policies.",
        enabled=True,
    )

    assert registry.get("finance_policies") == Domain(
        id="finance_policies",
        name="Finance Policies",
        description="Finance policies.",
        enabled=False,
    )

    assert [domain.id for domain in registry.list_enabled()] == ["employee_policies"]
