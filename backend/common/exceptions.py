"""
RAGOps common exception hierarchy.

This module defines the base exception hierarchy used throughout the
platform. The exceptions are framework-independent and can be translated
into HTTP, gRPC, CLI or background worker responses by the respective
adapter layer.

Author:
    RAGOps Development Team
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

# ============================================================================
# Error Codes
# ============================================================================


@dataclass(frozen=True, slots=True)
class ErrorCode:
    """
    Represents a platform error code.

    Example:
        COMMON-001
        AUTH-004
        VECTOR-010
    """

    code: str
    description: str


UNKNOWN_ERROR = ErrorCode("COMMON-000", "Unknown error")
VALIDATION_ERROR = ErrorCode("COMMON-001", "Validation failed")
CONFIGURATION_ERROR = ErrorCode("COMMON-002", "Configuration error")
NOT_FOUND_ERROR = ErrorCode("COMMON-003", "Resource not found")
CONFLICT_ERROR = ErrorCode("COMMON-004", "Resource conflict")
AUTHENTICATION_ERROR = ErrorCode("AUTH-001", "Authentication failed")
AUTHORIZATION_ERROR = ErrorCode("AUTH-002", "Access denied")
EXTERNAL_SERVICE_ERROR = ErrorCode("COMMON-005", "External service failure")
TIMEOUT_ERROR = ErrorCode("COMMON-006", "Operation timed out")


# ============================================================================
# Base Exception
# ============================================================================


class RAGOpsError(Exception):
    """
    Base exception for the platform.

    Every custom exception should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: ErrorCode = UNKNOWN_ERROR,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize exception into a JSON-compatible dictionary.
        """
        return {
            "error": self.error_code.code,
            "description": self.error_code.description,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }

    def __str__(self) -> str:
        return f"[{self.error_code.code}] {self.message}"


# ============================================================================
# Validation
# ============================================================================


class ValidationError(RAGOpsError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            error_code=VALIDATION_ERROR,
            status_code=400,
            details=details,
        )


# ============================================================================
# Configuration
# ============================================================================


class ConfigurationError(RAGOpsError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            error_code=CONFIGURATION_ERROR,
            status_code=500,
        )


# ============================================================================
# Resource Not Found
# ============================================================================


class ResourceNotFoundError(RAGOpsError):
    """Raised when a resource cannot be found."""

    def __init__(self, resource: str, identifier: Any) -> None:
        super().__init__(
            f"{resource} '{identifier}' was not found.",
            error_code=NOT_FOUND_ERROR,
            status_code=404,
            details={
                "resource": resource,
                "identifier": identifier,
            },
        )


# ============================================================================
# Conflict
# ============================================================================


class ResourceConflictError(RAGOpsError):
    """Raised when a resource already exists."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            error_code=CONFLICT_ERROR,
            status_code=409,
        )


# ============================================================================
# Authentication
# ============================================================================


class AuthenticationError(RAGOpsError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(
            message,
            error_code=AUTHENTICATION_ERROR,
            status_code=401,
        )


class AuthorizationError(RAGOpsError):
    """Raised when access is denied."""

    def __init__(self, message: str = "Access denied.") -> None:
        super().__init__(
            message,
            error_code=AUTHORIZATION_ERROR,
            status_code=403,
        )


# ============================================================================
# External Services
# ============================================================================


class ExternalServiceError(RAGOpsError):
    """Raised when an external dependency fails."""

    def __init__(
        self,
        service: str,
        message: str,
    ) -> None:
        super().__init__(
            message,
            error_code=EXTERNAL_SERVICE_ERROR,
            status_code=502,
            details={
                "service": service,
            },
        )


class OperationTimeoutError(RAGOpsError):
    """Raised when an operation times out."""

    def __init__(
        self,
        operation: str,
    ) -> None:
        super().__init__(
            f"{operation} timed out.",
            error_code=TIMEOUT_ERROR,
            status_code=504,
            details={
                "operation": operation,
            },
        )


# ============================================================================
# Utilities
# ============================================================================


def error_code_dict() -> dict[str, dict[str, str]]:
    """
    Returns all built-in platform error codes.

    Useful for documentation generation.
    """
    codes = [
        UNKNOWN_ERROR,
        VALIDATION_ERROR,
        CONFIGURATION_ERROR,
        NOT_FOUND_ERROR,
        CONFLICT_ERROR,
        AUTHENTICATION_ERROR,
        AUTHORIZATION_ERROR,
        EXTERNAL_SERVICE_ERROR,
        TIMEOUT_ERROR,
    ]

    return {item.code: asdict(item) for item in codes}


__all__ = [
    "ErrorCode",
    "RAGOpsError",
    "ValidationError",
    "ConfigurationError",
    "ResourceNotFoundError",
    "ResourceConflictError",
    "AuthenticationError",
    "AuthorizationError",
    "ExternalServiceError",
    "OperationTimeoutError",
    "UNKNOWN_ERROR",
    "VALIDATION_ERROR",
    "CONFIGURATION_ERROR",
    "NOT_FOUND_ERROR",
    "CONFLICT_ERROR",
    "AUTHENTICATION_ERROR",
    "AUTHORIZATION_ERROR",
    "EXTERNAL_SERVICE_ERROR",
    "TIMEOUT_ERROR",
    "error_code_dict",
]
