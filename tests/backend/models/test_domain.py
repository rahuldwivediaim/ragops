"""
Tests for the persistent Domain SQLAlchemy model.
"""

from sqlalchemy import inspect

from backend.models.domain import Domain
from backend.models.enums import DomainStatus
from backend.models.tenant import Tenant


def _create_tenant() -> Tenant:
    """Create an unsaved tenant for relationship tests."""

    return Tenant(
        code="ACME",
        name="Acme Corporation",
    )


def test_domain_table_name() -> None:
    """Domain should map to the domains table."""

    assert Domain.__tablename__ == "domains"


def test_root_domain_has_no_parent() -> None:
    """A newly created root domain should not have a parent."""

    domain = Domain(
        tenant=_create_tenant(),
        code="HR",
        name="Human Resources",
    )

    assert domain.parent_id is None
    assert domain.is_root is True


def test_child_domain_can_reference_parent() -> None:
    """A child domain should reference its parent domain."""

    tenant = _create_tenant()

    hr = Domain(
        tenant=tenant,
        code="HR",
        name="Human Resources",
    )

    payroll = Domain(
        tenant=tenant,
        code="PAYROLL",
        name="Payroll",
        parent=hr,
    )

    assert payroll.parent is hr
    assert payroll.parent_id == hr.id
    assert payroll.is_root is False


def test_parent_domain_contains_child() -> None:
    """Parent domain should expose its child domains."""

    tenant = _create_tenant()

    hr = Domain(
        tenant=tenant,
        code="HR",
        name="Human Resources",
    )

    payroll = Domain(
        tenant=tenant,
        code="PAYROLL",
        name="Payroll",
        parent=hr,
    )

    assert payroll in hr.children


def test_domain_can_have_no_description() -> None:
    """Domain description is optional."""

    domain = Domain(
        tenant=_create_tenant(),
        code="FINANCE",
        name="Finance",
    )

    assert domain.description is None


def test_domain_default_status_is_active() -> None:
    """Domain status column should define ACTIVE as the default."""

    column = Domain.__table__.c.status

    assert column.default is not None
    assert column.default.arg is DomainStatus.ACTIVE


def test_domain_has_expected_columns() -> None:
    """Domain should expose the canonical persistence columns."""

    columns = set(Domain.__table__.columns.keys())

    assert columns == {
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
        "tenant_id",
        "parent_id",
        "code",
        "name",
        "description",
        "status",
    }


def test_domain_has_tenant_foreign_key() -> None:
    """Domain must belong to a tenant."""

    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in Domain.__table__.c.tenant_id.foreign_keys
    }

    assert foreign_keys == {"tenants.id"}


def test_domain_has_parent_foreign_key() -> None:
    """Domain parent_id must reference domains.id."""

    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in Domain.__table__.c.parent_id.foreign_keys
    }

    assert foreign_keys == {"domains.id"}


def test_domain_has_self_parent_protection() -> None:
    """Domain metadata should prevent a domain from being its own parent."""

    check_constraints = {
        constraint.name
        for constraint in Domain.__table__.constraints
        if constraint.name is not None
    }

    assert "ck_domains_not_self_parent" in check_constraints


def test_domain_has_tenant_scoped_code_and_name_constraints() -> None:
    """Domain code and name should be unique within a tenant."""

    unique_constraints = {
        constraint.name
        for constraint in Domain.__table__.constraints
        if constraint.name is not None
    }

    assert "uq_domains_tenant_code" in unique_constraints
    assert "uq_domains_tenant_name" in unique_constraints


def test_domain_relationships_are_configured() -> None:
    """Domain should expose tenant, hierarchy and KB relationships."""

    relationships = inspect(Domain).relationships

    assert "tenant" in relationships
    assert "parent" in relationships
    assert "children" in relationships
    assert "knowledge_bases" in relationships
