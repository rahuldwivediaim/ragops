"""
Tests for DomainRepository.
"""

from uuid import uuid4
from unittest.mock import MagicMock

from backend.models.domain import Domain
from backend.repositories.domain_repository import DomainRepository


def _create_repository() -> tuple[DomainRepository, MagicMock]:
    """Create a repository with a mocked SQLAlchemy session."""

    session = MagicMock()
    repository = DomainRepository(session)

    return repository, session


def test_repository_uses_domain_model() -> None:
    """Repository should be configured with the Domain model."""

    repository, _ = _create_repository()

    assert repository._model is Domain


def test_get_by_code_is_tenant_scoped() -> None:
    """get_by_code should filter by tenant and domain code."""

    repository, session = _create_repository()

    tenant_id = uuid4()

    expected_domain = Domain(
        tenant_id=tenant_id,
        code="HR",
        name="Human Resources",
    )

    session.scalar.return_value = expected_domain

    result = repository.get_by_code(tenant_id, "HR")

    assert result is expected_domain
    session.scalar.assert_called_once()


def test_get_by_name_is_tenant_scoped() -> None:
    """get_by_name should filter by tenant and domain name."""

    repository, session = _create_repository()

    tenant_id = uuid4()

    expected_domain = Domain(
        tenant_id=tenant_id,
        code="HR",
        name="Human Resources",
    )

    session.scalar.return_value = expected_domain

    result = repository.get_by_name(
        tenant_id,
        "Human Resources",
    )

    assert result is expected_domain
    session.scalar.assert_called_once()


def test_exists_by_code_returns_true_when_domain_exists() -> None:
    """exists_by_code should return True for an existing domain."""

    repository, session = _create_repository()

    session.scalar.return_value = 1

    assert (
        repository.exists_by_code(
            uuid4(),
            "HR",
        )
        is True
    )


def test_exists_by_code_returns_false_when_domain_does_not_exist() -> None:
    """exists_by_code should return False when no domain exists."""

    repository, session = _create_repository()

    session.scalar.return_value = 0

    assert (
        repository.exists_by_code(
            uuid4(),
            "HR",
        )
        is False
    )


def test_exists_by_name_returns_true_when_domain_exists() -> None:
    """exists_by_name should return True for an existing domain."""

    repository, session = _create_repository()

    session.scalar.return_value = 1

    assert (
        repository.exists_by_name(
            uuid4(),
            "Human Resources",
        )
        is True
    )


def test_exists_by_name_returns_false_when_domain_does_not_exist() -> None:
    """exists_by_name should return False when no domain exists."""

    repository, session = _create_repository()

    session.scalar.return_value = 0

    assert (
        repository.exists_by_name(
            uuid4(),
            "Human Resources",
        )
        is False
    )


def test_get_root_domains_returns_domains() -> None:
    """get_root_domains should return root domains."""

    repository, session = _create_repository()

    domains = [
        Domain(
            tenant_id=uuid4(),
            code="FINANCE",
            name="Finance",
        ),
    ]

    session.scalars.return_value.all.return_value = domains

    result = repository.get_root_domains(uuid4())

    assert result == domains
    session.scalars.assert_called_once()


def test_get_children_returns_direct_children() -> None:
    """get_children should return direct child domains."""

    repository, session = _create_repository()

    domains = [
        Domain(
            tenant_id=uuid4(),
            code="PAYROLL",
            name="Payroll",
        ),
    ]

    session.scalars.return_value.all.return_value = domains

    result = repository.get_children(
        uuid4(),
        uuid4(),
    )

    assert result == domains
    session.scalars.assert_called_once()


def test_get_active_returns_active_domains() -> None:
    """get_active should return active domains."""

    repository, session = _create_repository()

    domains = [
        Domain(
            tenant_id=uuid4(),
            code="HR",
            name="Human Resources",
        ),
    ]

    session.scalars.return_value.all.return_value = domains

    result = repository.get_active(uuid4())

    assert result == domains
    session.scalars.assert_called_once()


def test_get_all_ordered_returns_tenant_domains() -> None:
    """get_all_ordered should return domains belonging to the tenant."""

    repository, session = _create_repository()

    domains = [
        Domain(
            tenant_id=uuid4(),
            code="FINANCE",
            name="Finance",
        ),
        Domain(
            tenant_id=uuid4(),
            code="HR",
            name="Human Resources",
        ),
    ]

    session.scalars.return_value.all.return_value = domains

    result = repository.get_all_ordered(uuid4())

    assert result == domains
    session.scalars.assert_called_once()
