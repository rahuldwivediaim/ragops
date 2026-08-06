"""
backend/common/__init__.py

Public API for the RAGOps common package.
"""

from .metadata import (
    AuditMetadata,
    ChunkMetadata,
    DocumentMetadata,
    PageMetadata,
    ResponseMetadata,
)
from .pagination import PaginationInfo, PaginationRequest
from .responses import (
    ApiError,
    ApiResponse,
    PaginatedResponse,
)
from .version import VERSION

__all__ = [
    "VERSION",
    "ApiError",
    "ApiResponse",
    "PaginatedResponse",
    "AuditMetadata",
    "ChunkMetadata",
    "DocumentMetadata",
    "PageMetadata",
    "ResponseMetadata",
    "PaginationInfo",
    "PaginationRequest",
]
