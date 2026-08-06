"""
backend/common/uuid.py

Enterprise UUID and semantic identifier helpers.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from .types import (
    ChunkId,
    CorrelationId,
    DocumentId,
    JobId,
    RequestId,
    SessionId,
    TaskId,
    TenantId,
    UserId,
    VectorId,
    WorkflowId,
)


def generate_uuid() -> UUID:
    """Generate a UUID4 object."""
    return uuid4()


def generate_uuid_str() -> str:
    """Generate a UUID4 string."""
    return str(uuid4())


def generate_id(prefix: str) -> str:
    """Generate a prefixed identifier."""
    return f"{prefix}_{uuid4().hex}"


def document_id() -> DocumentId:
    return DocumentId(generate_id("doc"))


def chunk_id() -> ChunkId:
    return ChunkId(generate_id("chunk"))


def vector_id() -> VectorId:
    return VectorId(generate_id("vec"))


def request_id() -> RequestId:
    return RequestId(generate_id("req"))


def correlation_id() -> CorrelationId:
    return CorrelationId(generate_id("corr"))


def user_id() -> UserId:
    return UserId(generate_id("usr"))


def session_id() -> SessionId:
    return SessionId(generate_id("sess"))


def tenant_id() -> TenantId:
    return TenantId(generate_id("tenant"))


def workflow_id() -> WorkflowId:
    return WorkflowId(generate_id("wf"))


def job_id() -> JobId:
    return JobId(generate_id("job"))


def task_id() -> TaskId:
    return TaskId(generate_id("task"))


__all__ = [
    "generate_uuid",
    "generate_uuid_str",
    "generate_id",
    "document_id",
    "chunk_id",
    "vector_id",
    "request_id",
    "correlation_id",
    "user_id",
    "session_id",
    "tenant_id",
    "workflow_id",
    "job_id",
    "task_id",
]
