"""
Tests for the persistent DomainRegistry.
"""

from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from backend.domains.registry.domain_registry import DomainRegistry
from backend.models.domain import Domain
from backend.models.enums import DomainStatus


def _domain(
    tenant_id: UUID,
    *,
    code: str,
    name: str,
    parent_id: UUID | None = None,
    status: DomainStatus = DomainStatus.ACTIVE,
) -> Domain:
    """Create a Domain test object."""

    domain = Domain(
        tenant_id=tenant_id,
        code=code,
        name=name,
        parent_id=parent_id,
        status=status,
    )
    domain.id = uuid4()

    return domain


@pytest.fixture
def tenant_id() -> UUID:
    """Return a test tenant ID."""

    return uuid4()


@pytest.fixture
def repository() -> MagicMock:
    """Return a mocked DomainRepository."""

    return MagicMock()


@pytest.fixture
def registry(
    repository: MagicMock,
    tenant_id: UUID,
) -> DomainRegistry:
    """Return a DomainRegistry using a mocked repository."""

    registry = DomainRegistry(
        MagicMock(),
        tenant_id,
    )
    registry._repository = repository

    return registry


def test_registry_get_returns_domain(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """Registry should return a tenant-scoped persisted domain."""

    domain = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )

    repository.get_by_id.return_value = domain

    result = registry.get(domain.id)

    assert result is domain
    repository.get_by_id.assert_called_once_with(
        tenant_id,
        domain.id,
    )


def test_registry_get_rejects_unknown_domain(
    registry: DomainRegistry,
    repository: MagicMock,
) -> None:
    """Unknown domains should raise KeyError."""

    domain_id = uuid4()

    repository.get_by_id.return_value = None

    with pytest.raises(
        KeyError,
        match="is not registered",
    ):
        registry.get(domain_id)


def test_registry_exists_returns_true_for_existing_domain(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """exists should return True for an existing domain."""

    domain = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )

    repository.get_by_id.return_value = domain

    assert registry.exists(domain.id) is True


def test_registry_exists_returns_false_for_unknown_domain(
    registry: DomainRegistry,
    repository: MagicMock,
) -> None:
    """exists should return False for an unknown domain."""

    repository.get_by_id.return_value = None

    assert registry.exists(uuid4()) is False


def test_registry_lists_all_domains(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """Registry should return all domains for its tenant."""

    employee = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )
    finance = _domain(
        tenant_id,
        code="FINANCE",
        name="Finance",
    )

    repository.get_all_ordered.return_value = [
        employee,
        finance,
    ]

    result = registry.list_all()

    assert result == [
        employee,
        finance,
    ]

    repository.get_all_ordered.assert_called_once_with(
        tenant_id,
    )


def test_registry_lists_only_effectively_enabled_domains(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """An inactive ancestor should disable an otherwise active child."""

    hr = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
        status=DomainStatus.INACTIVE,
    )

    payroll = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=hr.id,
        status=DomainStatus.ACTIVE,
    )

    repository.get_active.return_value = [payroll]

    repository.get_by_id.side_effect = lambda _tenant_id, domain_id: {
        hr.id: hr,
        payroll.id: payroll,
    }.get(domain_id)

    assert registry.list_enabled() == []


def test_registry_lists_direct_children(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """Registry should return direct children."""

    hr = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )

    payroll = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=hr.id,
    )

    benefits = _domain(
        tenant_id,
        code="BENEFITS",
        name="Benefits",
        parent_id=hr.id,
    )

    repository.get_by_id.return_value = hr
    repository.get_children.return_value = [
        payroll,
        benefits,
    ]

    result = registry.list_children(hr.id)

    assert result == [
        payroll,
        benefits,
    ]

    repository.get_children.assert_called_once_with(
        tenant_id,
        hr.id,
    )


def test_registry_lists_all_descendants(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """Registry should return all descendants breadth-first."""

    hr = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )

    payroll = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=hr.id,
    )

    benefits = _domain(
        tenant_id,
        code="BENEFITS",
        name="Benefits",
        parent_id=hr.id,
    )

    tax = _domain(
        tenant_id,
        code="TAX",
        name="Tax",
        parent_id=payroll.id,
    )

    domains = {
        hr.id: hr,
        payroll.id: payroll,
        benefits.id: benefits,
        tax.id: tax,
    }

    repository.get_by_id.side_effect = lambda _tenant_id, domain_id: domains.get(
        domain_id
    )

    repository.get_children.side_effect = lambda _tenant_id, parent_id: {
        hr.id: [payroll, benefits],
        payroll.id: [tax],
        benefits.id: [],
        tax.id: [],
    }.get(parent_id, [])

    result = registry.list_descendants(hr.id)

    assert result == [
        payroll,
        benefits,
        tax,
    ]


def test_registry_can_determine_descendant_relationship(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """Registry should determine ancestor/descendant relationships."""

    hr = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )

    payroll = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=hr.id,
    )

    tax = _domain(
        tenant_id,
        code="TAX",
        name="Tax",
        parent_id=payroll.id,
    )

    domains = {
        hr.id: hr,
        payroll.id: payroll,
        tax.id: tax,
    }

    repository.get_by_id.side_effect = lambda _tenant_id, domain_id: domains.get(
        domain_id
    )

    assert (
        registry.is_descendant(
            payroll.id,
            hr.id,
        )
        is True
    )

    assert (
        registry.is_descendant(
            tax.id,
            hr.id,
        )
        is True
    )

    assert (
        registry.is_descendant(
            hr.id,
            tax.id,
        )
        is False
    )

    assert (
        registry.is_descendant(
            hr.id,
            hr.id,
        )
        is False
    )


def test_registry_returns_domain_path(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """Registry should return the hierarchy path from root to domain."""

    hr = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )

    payroll = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=hr.id,
    )

    tax = _domain(
        tenant_id,
        code="TAX",
        name="Tax",
        parent_id=payroll.id,
    )

    domains = {
        hr.id: hr,
        payroll.id: payroll,
        tax.id: tax,
    }

    repository.get_by_id.side_effect = lambda _tenant_id, domain_id: domains.get(
        domain_id
    )

    assert registry.get_path_ids(tax.id) == (
        hr.id,
        payroll.id,
        tax.id,
    )

    assert registry.get_depth(hr.id) == 1
    assert registry.get_depth(payroll.id) == 2
    assert registry.get_depth(tax.id) == 3


def test_registry_can_include_self_in_descendants(
    registry: DomainRegistry,
    repository: MagicMock,
    tenant_id: UUID,
) -> None:
    """Registry should optionally include the requested domain."""

    hr = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )

    payroll = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=hr.id,
    )

    domains = {
        hr.id: hr,
        payroll.id: payroll,
    }

    repository.get_by_id.side_effect = lambda _tenant_id, domain_id: domains.get(
        domain_id
    )

    repository.get_children.side_effect = lambda _tenant_id, parent_id: {
        hr.id: [payroll],
        payroll.id: [],
    }.get(parent_id, [])

    result = registry.list_descendants(
        hr.id,
        include_self=True,
    )

    assert result == [
        hr,
        payroll,
    ]
