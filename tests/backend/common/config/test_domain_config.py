"""
Tests for domain configuration.
"""

import pytest
from pydantic import ValidationError

from backend.common.config.domains import DomainConfig


def test_domain_config_creation() -> None:
    config = DomainConfig(
        name="Employee Policies",
        description="Employee HR policies.",
    )

    assert config.name == "Employee Policies"
    assert config.description == "Employee HR policies."
    assert config.enabled is True
    assert config.parent_id is None
    assert config.is_root is True


def test_domain_config_can_be_disabled() -> None:
    config = DomainConfig(
        name="Finance Policies",
        description="Finance policies.",
        enabled=False,
    )

    assert config.enabled is False


def test_domain_config_can_have_parent() -> None:
    config = DomainConfig(
        name="Payroll",
        description="Payroll policies.",
        parent_id="hr",
    )

    assert config.parent_id == "hr"
    assert config.is_root is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("name", "   "),
        ("description", ""),
        ("description", "   "),
    ],
)
def test_domain_config_rejects_empty_values(
    field: str,
    value: str,
) -> None:
    if field == "name":
        with pytest.raises(ValueError):
            DomainConfig(
                name=value,
                description="Employee HR policies.",
            )
    else:
        with pytest.raises(ValueError):
            DomainConfig(
                name="Employee Policies",
                description=value,
            )


def test_domain_config_rejects_empty_parent_id() -> None:
    with pytest.raises(ValueError):
        DomainConfig(
            name="Payroll",
            description="Payroll policies.",
            parent_id="   ",
        )


def test_domain_config_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        DomainConfig.model_validate(
            {
                "name": "Employee Policies",
                "description": "Employee HR policies.",
                "unknown_field": "value",
            }
        )
