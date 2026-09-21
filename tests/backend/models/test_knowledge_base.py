"""
Tests for the persistent Knowledge Base SQLAlchemy model.
"""

from sqlalchemy import inspect

from backend.models.domain import Domain
from backend.models.enums import KnowledgeBaseStatus
from backend.models.knowledge_base import KnowledgeBase
from backend.models.tenant import Tenant


def _create_tenant() -> Tenant:
    """Create an unsaved tenant for relationship tests."""

    return Tenant(
        code="ACME",
        name="Acme Corporation",
    )


def _create_domain(tenant: Tenant) -> Domain:
    """Create an unsaved domain for Knowledge Base tests."""

    return Domain(
        tenant=tenant,
        code="HR",
        name="Human Resources",
    )


def test_knowledge_base_table_name() -> None:
    """Knowledge Base should map to the knowledge_bases table."""

    assert KnowledgeBase.__tablename__ == "knowledge_bases"


def test_knowledge_base_requires_domain() -> None:
    """Knowledge Base domain_id must be non-nullable."""

    column = KnowledgeBase.__table__.c.domain_id

    assert column.nullable is False


def test_knowledge_base_requires_tenant() -> None:
    """Knowledge Base tenant_id must be non-nullable."""

    column = KnowledgeBase.__table__.c.tenant_id

    assert column.nullable is False


def test_knowledge_base_can_be_created_for_domain() -> None:
    """Knowledge Base should belong to a tenant and domain."""

    tenant = _create_tenant()
    domain = _create_domain(tenant)

    knowledge_base = KnowledgeBase(
        tenant=tenant,
        domain=domain,
        code="HR_POLICIES",
        name="HR Policies",
        description="Human Resources policies.",
    )

    assert knowledge_base.tenant is tenant
    assert knowledge_base.domain is domain
    assert knowledge_base.code == "HR_POLICIES"
    assert knowledge_base.name == "HR Policies"
    assert knowledge_base.description == "Human Resources policies."


def test_knowledge_base_default_status_is_active() -> None:
    """Knowledge Base status column should define ACTIVE as the default."""

    column = KnowledgeBase.__table__.c.status

    assert column.default is not None
    assert column.default.arg is KnowledgeBaseStatus.ACTIVE


def test_knowledge_base_default_language_is_english() -> None:
    """Knowledge Base should default to English."""

    column = KnowledgeBase.__table__.c.default_language

    assert column.default is not None
    assert column.default.arg == "en"


def test_knowledge_base_has_expected_columns() -> None:
    """Knowledge Base should expose the canonical persistence columns."""

    columns = set(KnowledgeBase.__table__.columns.keys())

    assert columns == {
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
        "tenant_id",
        "domain_id",
        "code",
        "name",
        "description",
        "status",
        "owner",
        "default_language",
    }


def test_knowledge_base_has_tenant_foreign_key() -> None:
    """Knowledge Base must reference its tenant."""

    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in KnowledgeBase.__table__.c.tenant_id.foreign_keys
    }

    assert foreign_keys == {"tenants.id"}


def test_knowledge_base_has_domain_foreign_key() -> None:
    """Knowledge Base must reference its domain."""

    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in KnowledgeBase.__table__.c.domain_id.foreign_keys
    }

    assert foreign_keys == {"domains.id"}


def test_knowledge_base_has_tenant_scoped_code_and_name_constraints() -> None:
    """Knowledge Base code and name should be unique within a tenant."""

    unique_constraints = {
        constraint.name
        for constraint in KnowledgeBase.__table__.constraints
        if constraint.name is not None
    }

    assert "uq_knowledge_bases_tenant_code" in unique_constraints
    assert "uq_knowledge_bases_tenant_name" in unique_constraints


def test_knowledge_base_relationships_are_configured() -> None:
    """Knowledge Base should expose tenant, domain and document relationships."""

    relationships = inspect(KnowledgeBase).relationships

    assert "tenant" in relationships
    assert "domain" in relationships
    assert "documents" in relationships


def test_knowledge_base_does_not_duplicate_parent_domain_id() -> None:
    """
    Knowledge Base should store only its direct domain.

    Parent domain information is derived through the Domain hierarchy.
    """

    columns = set(KnowledgeBase.__table__.columns.keys())

    assert "parent_id" not in columns
    assert "parent_domain_id" not in columns
