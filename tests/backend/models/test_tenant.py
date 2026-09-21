"""
Tests for the persistent Tenant SQLAlchemy model.
"""

from sqlalchemy import inspect

from backend.models.enums import TenantStatus
from backend.models.tenant import Tenant


def test_tenant_table_name() -> None:
    """Tenant should map to the tenants table."""

    assert Tenant.__tablename__ == "tenants"


def test_tenant_creation_uses_expected_values() -> None:
    """Tenant should preserve supplied business values."""

    tenant = Tenant(
        code="ACME",
        name="Acme Corporation",
        description="Acme Corporation tenant.",
    )

    assert tenant.code == "ACME"
    assert tenant.name == "Acme Corporation"
    assert tenant.description == "Acme Corporation tenant."


def test_tenant_default_status_is_active() -> None:
    """Tenant status column should define ACTIVE as its default."""

    column = Tenant.__table__.c.status

    assert column.default is not None
    assert column.default.arg is TenantStatus.ACTIVE


def test_tenant_has_expected_columns() -> None:
    """Tenant should expose the canonical persistence columns."""

    columns = set(Tenant.__table__.columns.keys())

    assert columns == {
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
        "code",
        "name",
        "description",
        "status",
    }


def test_tenant_code_is_unique() -> None:
    """Tenant code should be globally unique."""

    unique_constraints = {
        constraint.name
        for constraint in Tenant.__table__.constraints
        if constraint.name is not None
    }

    assert "uq_tenants_code" in unique_constraints


def test_tenant_relationships_are_configured() -> None:
    """Tenant should expose Domain and Knowledge Base collections."""

    relationships = inspect(Tenant).relationships

    assert "domains" in relationships
    assert "knowledge_bases" in relationships
