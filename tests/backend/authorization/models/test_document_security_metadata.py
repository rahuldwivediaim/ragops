"""
Tests for document security metadata.
"""

import pytest
from pydantic import ValidationError

from backend.authorization.models import (
    DocumentClassification,
    DocumentSecurityMetadata,
)


def create_metadata() -> DocumentSecurityMetadata:
    """Create representative document security metadata."""

    return DocumentSecurityMetadata(
        tenant_id="default",
        document_id="employee_policy",
        document_version_id="employee_policy_v1",
        domain_id="employee_policies",
        knowledge_base_id="employee_kb",
        classification=DocumentClassification.PUBLIC,
        access_policy_ids=frozenset(
            {"employee_access"},
        ),
    )


def test_document_security_metadata_creation() -> None:
    metadata = create_metadata()

    assert metadata.tenant_id == "default"
    assert metadata.document_id == "employee_policy"
    assert metadata.document_version_id == "employee_policy_v1"
    assert metadata.domain_id == "employee_policies"
    assert metadata.knowledge_base_id == "employee_kb"
    assert metadata.classification is DocumentClassification.PUBLIC
    assert metadata.access_policy_ids == frozenset(
        {"employee_access"},
    )


def test_document_security_metadata_is_immutable() -> None:
    metadata = create_metadata()

    with pytest.raises(ValidationError):
        metadata.tenant_id = "other_tenant"  # type: ignore[misc]


def test_document_security_metadata_serializes_to_vector_metadata() -> None:
    metadata = create_metadata()

    vector_metadata = metadata.to_vector_metadata()

    assert vector_metadata == {
        "tenant_id": "default",
        "document_id": "employee_policy",
        "document_version_id": "employee_policy_v1",
        "domain_id": "employee_policies",
        "knowledge_base_id": "employee_kb",
        "classification": "public",
        "access_policy_ids": [
            "employee_access",
        ],
    }


def test_multiple_access_policies_are_serialized_as_sorted_list() -> None:
    metadata = DocumentSecurityMetadata(
        tenant_id="default",
        document_id="shared_policy",
        document_version_id="shared_policy_v1",
        domain_id="employee_policies",
        knowledge_base_id="employee_kb",
        classification=DocumentClassification.RESTRICTED,
        access_policy_ids=frozenset(
            {
                "hr_manager_access",
                "compliance_access",
            },
        ),
    )

    vector_metadata = metadata.to_vector_metadata()

    assert vector_metadata["access_policy_ids"] == [
        "compliance_access",
        "hr_manager_access",
    ]


@pytest.mark.parametrize(
    "field",
    [
        "tenant_id",
        "document_id",
        "document_version_id",
        "domain_id",
        "knowledge_base_id",
    ],
)
def test_security_metadata_rejects_empty_identifiers(
    field: str,
) -> None:
    values = {
        "tenant_id": "default",
        "document_id": "document",
        "document_version_id": "version",
        "domain_id": "employee",
        "knowledge_base_id": "employee_kb",
        "classification": DocumentClassification.PUBLIC,
        "access_policy_ids": frozenset(
            {"employee_access"},
        ),
    }

    values[field] = "   "

    with pytest.raises(ValidationError):
        DocumentSecurityMetadata(**values)


def test_security_metadata_rejects_empty_policy_set() -> None:
    with pytest.raises(
        ValidationError,
        match="at least one access policy",
    ):
        DocumentSecurityMetadata(
            tenant_id="default",
            document_id="employee_policy",
            document_version_id="employee_policy_v1",
            domain_id="employee",
            knowledge_base_id="employee_kb",
            classification=DocumentClassification.PUBLIC,
            access_policy_ids=frozenset(),
        )


def test_security_metadata_rejects_empty_policy_id() -> None:
    with pytest.raises(ValidationError):
        DocumentSecurityMetadata(
            tenant_id="default",
            document_id="employee_policy",
            document_version_id="employee_policy_v1",
            domain_id="employee",
            knowledge_base_id="employee_kb",
            classification=DocumentClassification.PUBLIC,
            access_policy_ids=frozenset(
                {
                    "employee_access",
                    "   ",
                },
            ),
        )


@pytest.mark.parametrize(
    "classification",
    [
        DocumentClassification.PUBLIC,
        DocumentClassification.RESTRICTED,
        DocumentClassification.CONFIDENTIAL,
    ],
)
def test_supported_document_classifications(
    classification: DocumentClassification,
) -> None:
    metadata = create_metadata().model_copy(
        update={
            "classification": classification,
        },
    )

    assert metadata.classification is classification
