"""
Document security metadata model.

Defines the canonical security metadata that must be propagated
from a document to every processing chunk and vector record.

This metadata is intentionally authorization-focused and is
independent of vector-store implementation details.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.authorization.models.document_classification import (
    DocumentClassification,
)


class DocumentSecurityMetadata(BaseModel):
    """
    Security metadata associated with a document.

    The same security metadata must be copied to every chunk
    generated from the document.

    Classification describes sensitivity.

    Access is determined by access policies.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    tenant_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    document_version_id: str = Field(min_length=1)
    domain_id: str = Field(min_length=1)
    knowledge_base_id: str = Field(min_length=1)
    classification: DocumentClassification
    access_policy_ids: frozenset[str] = frozenset()

    @field_validator(
        "tenant_id",
        "document_id",
        "document_version_id",
        "domain_id",
        "knowledge_base_id",
    )
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        """Reject identifiers containing only whitespace."""

        if not value.strip():
            raise ValueError(
                "Security metadata identifiers cannot be empty.",
            )

        return value

    @field_validator("access_policy_ids")
    @classmethod
    def validate_access_policy_ids(
        cls,
        value: frozenset[str],
    ) -> frozenset[str]:
        """Validate configured access-policy identifiers."""

        if not value:
            raise ValueError(
                "Document security metadata must contain at least one access policy.",
            )

        if any(not policy_id.strip() for policy_id in value):
            raise ValueError(
                "Access policy identifiers cannot be empty.",
            )

        return value

    def to_vector_metadata(self) -> dict[str, object]:
        """
        Convert security metadata into flat vector-store metadata.

        Policy identifiers are serialized as a list of strings so
        vector stores such as Pinecone can evaluate them using
        metadata filters.
        """

        return {
            "tenant_id": self.tenant_id,
            "document_id": self.document_id,
            "document_version_id": self.document_version_id,
            "domain_id": self.domain_id,
            "knowledge_base_id": self.knowledge_base_id,
            "classification": self.classification.value,
            "access_policy_ids": sorted(
                self.access_policy_ids,
            ),
        }


__all__ = ["DocumentSecurityMetadata"]
