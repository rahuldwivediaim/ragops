"""
RAGOps Platform Constants.

This module contains platform-wide constants that are shared across the
backend services. The goal is to eliminate magic numbers and hardcoded
strings from the codebase.

This module MUST NOT contain any business logic.

Author:
    RAGOps Development Team
"""

from __future__ import annotations

###############################################################################
# Platform
###############################################################################

PLATFORM_NAME: str = "RAGOps"

APPLICATION_NAME: str = "RAGOps Platform"

ORGANIZATION_NAME: str = "RAGOps"

###############################################################################
# Encoding
###############################################################################

DEFAULT_ENCODING: str = "utf-8"

###############################################################################
# HTTP
###############################################################################

HTTP_OK: int = 200
HTTP_CREATED: int = 201
HTTP_ACCEPTED: int = 202
HTTP_NO_CONTENT: int = 204

HTTP_BAD_REQUEST: int = 400
HTTP_UNAUTHORIZED: int = 401
HTTP_FORBIDDEN: int = 403
HTTP_NOT_FOUND: int = 404
HTTP_CONFLICT: int = 409
HTTP_UNPROCESSABLE_ENTITY: int = 422
HTTP_TOO_MANY_REQUESTS: int = 429

HTTP_INTERNAL_SERVER_ERROR: int = 500
HTTP_BAD_GATEWAY: int = 502
HTTP_SERVICE_UNAVAILABLE: int = 503
HTTP_GATEWAY_TIMEOUT: int = 504

###############################################################################
# API
###############################################################################

DEFAULT_API_PREFIX: str = "/api"

DEFAULT_API_VERSION: str = "v1"

###############################################################################
# Headers
###############################################################################

HEADER_REQUEST_ID: str = "X-Request-ID"

HEADER_CORRELATION_ID: str = "X-Correlation-ID"

HEADER_TRACE_ID: str = "X-Trace-ID"

HEADER_IDEMPOTENCY_KEY: str = "Idempotency-Key"

HEADER_CONTENT_TYPE: str = "Content-Type"

HEADER_ACCEPT: str = "Accept"

HEADER_AUTHORIZATION: str = "Authorization"

###############################################################################
# Content Types
###############################################################################

CONTENT_TYPE_JSON: str = "application/json"

CONTENT_TYPE_TEXT: str = "text/plain"

CONTENT_TYPE_HTML: str = "text/html"

CONTENT_TYPE_XML: str = "application/xml"

CONTENT_TYPE_PDF: str = "application/pdf"

CONTENT_TYPE_BINARY: str = "application/octet-stream"

###############################################################################
# Health
###############################################################################

STATUS_HEALTHY: str = "healthy"

STATUS_DEGRADED: str = "degraded"

STATUS_UNHEALTHY: str = "unhealthy"

###############################################################################
# Pagination
###############################################################################

DEFAULT_PAGE_NUMBER: int = 1

DEFAULT_PAGE_SIZE: int = 25

MAX_PAGE_SIZE: int = 100

###############################################################################
# Time
###############################################################################

SECONDS_PER_MINUTE: int = 60

MINUTES_PER_HOUR: int = 60

HOURS_PER_DAY: int = 24

SECONDS_PER_HOUR: int = 3600

SECONDS_PER_DAY: int = 86400

###############################################################################
# Timeouts (seconds)
###############################################################################

DEFAULT_REQUEST_TIMEOUT: int = 30

DEFAULT_DATABASE_TIMEOUT: int = 30

DEFAULT_HTTP_TIMEOUT: int = 60

DEFAULT_SHUTDOWN_TIMEOUT: int = 30

###############################################################################
# Retry
###############################################################################

DEFAULT_MAX_RETRIES: int = 3

DEFAULT_RETRY_DELAY_SECONDS: int = 2

###############################################################################
# UUID
###############################################################################

UUID4_LENGTH: int = 36

###############################################################################
# Logging
###############################################################################

DEFAULT_LOGGER_NAME: str = "ragops"

###############################################################################
# Environment Names
###############################################################################

ENV_DEVELOPMENT: str = "development"

ENV_TEST: str = "test"

ENV_STAGING: str = "staging"

ENV_PRODUCTION: str = "production"

###############################################################################
# Boolean Strings
###############################################################################

TRUE_VALUES: tuple[str, ...] = (
    "true",
    "1",
    "yes",
    "y",
    "on",
)

FALSE_VALUES: tuple[str, ...] = (
    "false",
    "0",
    "no",
    "n",
    "off",
)

###############################################################################
# Date Formats
###############################################################################

ISO8601_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

DATE_FORMAT: str = "%Y-%m-%d"

TIME_FORMAT: str = "%H:%M:%S"

###############################################################################
# Miscellaneous
###############################################################################

EMPTY_STRING: str = ""

SPACE: str = " "

COMMA: str = ","

COLON: str = ":"

SEMICOLON: str = ";"

FORWARD_SLASH: str = "/"

BACKWARD_SLASH: str = "\\"

NEW_LINE: str = "\n"

TAB: str = "\t"

###############################################################################
# Exported Symbols
###############################################################################

__all__ = [name for name in globals() if name.isupper() and not name.startswith("_")]
