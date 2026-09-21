"""
Tests for DomainService.
"""

from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from backend.domains.service.domain_service import DomainService
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

    return Domain(
        tenant_id=tenant_id,
        code=code,
        name=name,
        parent_id=parent_id,
        status=status,
    )


@pytest.fixture
def tenant_id() -> UUID:
    """Return a test tenant ID."""

    return uuid4()


@pytest.fixture
def service() -> DomainService:
    """Return a DomainService with a mocked repository."""

    service = DomainService(MagicMock())
    service._repository = MagicMock()
    return service


def test_create_root_domain(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A root domain should be created without a parent."""

    created = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )

    service._repository.exists_by_code.return_value = False
    service._repository.get_by_name.return_value = None
    service._repository.create.return_value = created

    result = service.create(
        tenant_id=tenant_id,
        code="HR",
        name="Human Resources",
    )

    assert result is created
    service._repository.create.assert_called_once()


def test_create_child_domain(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A domain should be able to reference a valid parent."""

    parent_id = uuid4()

    parent = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )
    parent.id = parent_id

    created = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=parent_id,
    )

    service._repository.exists_by_code.return_value = False
    service._repository.get_by_name.return_value = None
    service._repository.get_by_id.return_value = parent
    service._repository.create.return_value = created

    result = service.create(
        tenant_id=tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=parent_id,
    )

    assert result is created
    service._repository.create.assert_called_once()


def test_create_rejects_duplicate_code(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A duplicate domain code should be rejected."""

    service._repository.exists_by_code.return_value = True

    with pytest.raises(
        ValueError,
        match="Domain code 'HR' already exists",
    ):
        service.create(
            tenant_id=tenant_id,
            code="HR",
            name="Human Resources",
        )


def test_create_rejects_duplicate_name(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A duplicate domain name should be rejected."""

    existing_domain = _domain(
        tenant_id,
        code="EXISTING",
        name="Human Resources",
    )
    existing_domain.id = uuid4()

    service._repository.exists_by_code.return_value = False
    service._repository.get_by_name.return_value = existing_domain

    with pytest.raises(
        ValueError,
        match="Domain name 'Human Resources' already exists",
    ):
        service.create(
            tenant_id=tenant_id,
            code="HR",
            name="Human Resources",
        )


def test_create_rejects_unknown_parent(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A parent from outside the tenant or a missing parent is rejected."""

    parent_id = uuid4()

    service._repository.exists_by_code.return_value = False
    service._repository.get_by_name.return_value = None
    service._repository.get_by_id.return_value = None

    with pytest.raises(
        ValueError,
        match="does not exist within the tenant",
    ):
        service.create(
            tenant_id=tenant_id,
            code="PAYROLL",
            name="Payroll",
            parent_id=parent_id,
        )


def test_create_rejects_fourth_level(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A fourth hierarchy level should be rejected."""

    level_1 = _domain(
        tenant_id,
        code="HR",
        name="HR",
    )
    level_1.id = uuid4()

    level_2 = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=level_1.id,
    )
    level_2.id = uuid4()

    level_3 = _domain(
        tenant_id,
        code="TAX",
        name="Tax",
        parent_id=level_2.id,
    )
    level_3.id = uuid4()

    domains = {
        level_1.id: level_1,
        level_2.id: level_2,
        level_3.id: level_3,
    }

    service._repository.exists_by_code.return_value = False
    service._repository.get_by_name.return_value = None
    service._repository.get_by_id.side_effect = (
        lambda _tenant_id, domain_id: domains.get(domain_id)
    )

    with pytest.raises(
        ValueError,
        match="maximum domain hierarchy depth of 3",
    ):
        service.create(
            tenant_id=tenant_id,
            code="STATE_TAX",
            name="State Tax",
            parent_id=level_3.id,
        )


def test_update_rejects_self_parent(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A domain cannot reference itself as its parent."""

    domain_id = uuid4()

    domain = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )
    domain.id = domain_id

    service._repository.get_by_id_or_raise.return_value = domain

    with pytest.raises(
        ValueError,
        match="cannot be its own parent",
    ):
        service.update(
            tenant_id,
            domain_id,
            parent_id=domain_id,
        )


def test_update_rejects_cycle(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """Moving a domain below one of its descendants should be rejected."""

    hr_id = uuid4()
    payroll_id = uuid4()

    hr = _domain(
        tenant_id,
        code="HR",
        name="HR",
    )
    hr.id = hr_id

    payroll = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=hr_id,
    )
    payroll.id = payroll_id

    domains = {
        hr_id: hr,
        payroll_id: payroll,
    }

    service._repository.get_by_id_or_raise.return_value = hr
    service._repository.get_by_id.side_effect = (
        lambda _tenant_id, domain_id: domains.get(domain_id)
    )

    with pytest.raises(
        ValueError,
        match="hierarchy cycle",
    ):
        service.update(
            tenant_id,
            hr_id,
            parent_id=payroll_id,
        )


def test_deactivate_domain(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """Deactivating a domain should set its status to INACTIVE."""

    domain_id = uuid4()

    domain = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )
    domain.id = domain_id

    service._repository.get_by_id_or_raise.return_value = domain
    service._repository.update.return_value = domain

    result = service.deactivate(
        tenant_id,
        domain_id,
    )

    assert result.status is DomainStatus.INACTIVE
    service._repository.update.assert_called_once_with(domain)


def test_activate_domain(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """Activating a domain should set its status to ACTIVE."""

    domain_id = uuid4()

    domain = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
        status=DomainStatus.INACTIVE,
    )
    domain.id = domain_id

    service._repository.get_by_id_or_raise.return_value = domain
    service._repository.update.return_value = domain

    result = service.activate(
        tenant_id,
        domain_id,
    )

    assert result.status is DomainStatus.ACTIVE
    service._repository.update.assert_called_once_with(domain)


def test_delete_rejects_domain_with_children(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A domain with children should not be deleted."""

    domain_id = uuid4()

    domain = _domain(
        tenant_id,
        code="HR",
        name="Human Resources",
    )
    domain.id = domain_id

    child = _domain(
        tenant_id,
        code="PAYROLL",
        name="Payroll",
        parent_id=domain_id,
    )

    service._repository.get_by_id_or_raise.return_value = domain
    service._repository.get_children.return_value = [child]

    with pytest.raises(
        ValueError,
        match="has child domains",
    ):
        service.delete(
            tenant_id,
            domain_id,
        )


def test_delete_leaf_domain(
    service: DomainService,
    tenant_id: UUID,
) -> None:
    """A leaf domain should be deletable."""

    domain_id = uuid4()

    domain = _domain(
        tenant_id,
        code="PAYROLL_TAX",
        name="Payroll Tax",
    )
    domain.id = domain_id

    service._repository.get_by_id_or_raise.return_value = domain
    service._repository.get_children.return_value = []

    service.delete(
        tenant_id,
        domain_id,
    )

    service._repository.delete.assert_called_once_with(domain)
