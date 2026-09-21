"""
Tests for the Domain model.
"""

from dataclasses import FrozenInstanceError

import pytest

from backend.domains.models.domain import Domain


def test_domain_creation() -> None:
    domain = Domain(
        id="employee_policies",
        name="Employee Policies",
        description=("Employee HR policies including leave, attendance and benefits."),
    )

    assert domain.id == "employee_policies"
    assert domain.name == "Employee Policies"
    assert (
        domain.description
        == "Employee HR policies including leave, attendance and benefits."
    )
    assert domain.enabled is True
    assert domain.parent_id is None
    assert domain.is_root is True


def test_domain_can_be_disabled() -> None:
    domain = Domain(
        id="finance_policies",
        name="Finance Policies",
        description="Finance and expense policies.",
        enabled=False,
    )

    assert domain.enabled is False


def test_domain_can_have_parent() -> None:
    domain = Domain(
        id="payroll",
        name="Payroll",
        description="Payroll policies.",
        parent_id="hr",
    )

    assert domain.parent_id == "hr"
    assert domain.is_root is False


def test_domain_is_immutable() -> None:
    domain = Domain(
        id="employee_policies",
        name="Employee Policies",
        description="Employee policies.",
    )

    with pytest.raises(FrozenInstanceError):
        domain.enabled = False  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", ""),
        ("id", "   "),
        ("name", ""),
        ("name", "   "),
        ("description", ""),
        ("description", "   "),
    ],
)
def test_domain_rejects_empty_required_fields(
    field: str,
    value: str,
) -> None:
    if field == "id":
        with pytest.raises(ValueError):
            Domain(
                id=value,
                name="Employee Policies",
                description="Employee policies.",
            )

    elif field == "name":
        with pytest.raises(ValueError):
            Domain(
                id="employee_policies",
                name=value,
                description="Employee policies.",
            )

    else:
        with pytest.raises(ValueError):
            Domain(
                id="employee_policies",
                name="Employee Policies",
                description=value,
            )


def test_domain_rejects_empty_parent_id() -> None:
    with pytest.raises(ValueError):
        Domain(
            id="payroll",
            name="Payroll",
            description="Payroll policies.",
            parent_id="   ",
        )


def test_domain_rejects_itself_as_parent() -> None:
    with pytest.raises(ValueError):
        Domain(
            id="hr",
            name="HR",
            description="Human Resources.",
            parent_id="hr",
        )
