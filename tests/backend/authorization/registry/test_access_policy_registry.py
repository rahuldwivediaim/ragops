"""
Tests for the Access Policy Registry.
"""

import pytest

from backend.authorization.registry import AccessPolicyRegistry
from backend.common.config.authorization import AccessPolicyConfig


def test_access_policy_registry_can_lookup_policy() -> None:
    registry = AccessPolicyRegistry(
        policies={
            "employee_access": AccessPolicyConfig(
                domains=("employee_policies",),
                knowledge_bases=("employee_knowledge_base",),
            ),
        },
    )

    policy = registry.get("employee_access")

    assert policy.domains == ("employee_policies",)
    assert policy.knowledge_bases == ("employee_knowledge_base",)


def test_access_policy_registry_reports_existing_policy() -> None:
    registry = AccessPolicyRegistry(
        policies={
            "employee_access": AccessPolicyConfig(),
        },
    )

    assert registry.exists("employee_access") is True
    assert registry.exists("finance_access") is False


def test_access_policy_registry_lists_policy_ids() -> None:
    registry = AccessPolicyRegistry(
        policies={
            "employee_access": AccessPolicyConfig(),
            "finance_access": AccessPolicyConfig(),
        },
    )

    assert registry.list_ids() == (
        "employee_access",
        "finance_access",
    )


def test_access_policy_registry_unknown_policy_raises_key_error() -> None:
    registry = AccessPolicyRegistry(
        policies={
            "employee_access": AccessPolicyConfig(),
        },
    )

    with pytest.raises(
        KeyError,
        match="Unknown authorization policy: finance_access",
    ):
        registry.get("finance_access")


def test_access_policy_registry_length() -> None:
    registry = AccessPolicyRegistry(
        policies={
            "employee_access": AccessPolicyConfig(),
            "finance_access": AccessPolicyConfig(),
        },
    )

    assert len(registry) == 2
