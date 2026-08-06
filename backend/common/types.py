"""
backend/common/types.py

Shared enterprise type aliases, protocols and generic definitions.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, NewType, Protocol, TypeAlias, TypeVar, runtime_checkable

# ---------------------------------------------------------------------
# Semantic identifiers
# ---------------------------------------------------------------------

DocumentId = NewType("DocumentId", str)
ChunkId = NewType("ChunkId", str)
VectorId = NewType("VectorId", str)
RequestId = NewType("RequestId", str)
CorrelationId = NewType("CorrelationId", str)
UserId = NewType("UserId", str)
TenantId = NewType("TenantId", str)
WorkflowId = NewType("WorkflowId", str)
JobId = NewType("JobId", str)
TaskId = NewType("TaskId", str)
SessionId = NewType("SessionId", str)

# ---------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------

JSONPrimitive: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONPrimitive | list["JSONValue"] | dict[str, "JSONValue"]
JSONObject: TypeAlias = dict[str, JSONValue]
ReadonlyJSON: TypeAlias = Mapping[str, JSONValue]

# ---------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------

EmbeddingVector: TypeAlias = list[float]
EmbeddingBatch: TypeAlias = list[EmbeddingVector]

MetadataDict: TypeAlias = dict[str, Any]
Headers: TypeAlias = dict[str, str]
Tags: TypeAlias = dict[str, str]

# ---------------------------------------------------------------------
# Generics
# ---------------------------------------------------------------------

T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")

# ---------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------


@runtime_checkable
class SupportsId(Protocol):
    id: str


@runtime_checkable
class SupportsTenant(Protocol):
    tenant_id: TenantId


@runtime_checkable
class SupportsAudit(Protocol):
    created_at: Any
    updated_at: Any


@runtime_checkable
class SupportsOwner(Protocol):
    owner: str


@runtime_checkable
class SupportsVersion(Protocol):
    version: int


__all__ = [
    "ChunkId",
    "CorrelationId",
    "DocumentId",
    "EmbeddingBatch",
    "EmbeddingVector",
    "Headers",
    "JSONObject",
    "JSONPrimitive",
    "JSONValue",
    "JobId",
    "KT",
    "MetadataDict",
    "ReadonlyJSON",
    "RequestId",
    "SessionId",
    "SupportsAudit",
    "SupportsId",
    "SupportsOwner",
    "SupportsTenant",
    "SupportsVersion",
    "T",
    "Tags",
    "TaskId",
    "TenantId",
    "UserId",
    "VT",
    "VectorId",
    "WorkflowId",
]
