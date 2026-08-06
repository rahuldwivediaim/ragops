"""
Common enumerations used throughout the RAGOps platform.

This module centralizes all platform-wide enumerations to ensure
consistent values across services and eliminate hardcoded strings.

Author:
    RAGOps Development Team
"""

from __future__ import annotations

from enum import Enum, IntEnum, StrEnum, auto


class Environment(StrEnum):
    """Application runtime environments."""

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class HealthStatus(StrEnum):
    """Health status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class LogLevel(StrEnum):
    """Supported log levels."""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    TRACE = "TRACE"


class HttpMethod(StrEnum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class SortDirection(StrEnum):
    """Sorting direction."""

    ASC = "asc"
    DESC = "desc"


class ResponseStatus(StrEnum):
    """Standard API response status."""

    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


class TaskStatus(StrEnum):
    """Generic task lifecycle."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentStatus(StrEnum):
    """Document processing lifecycle."""

    UPLOADED = "uploaded"
    VALIDATING = "validating"
    VALIDATED = "validated"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ChunkStatus(StrEnum):
    """Document chunk status."""

    CREATED = "created"
    EMBEDDING = "embedding"
    INDEXED = "indexed"
    FAILED = "failed"


class EmbeddingProvider(StrEnum):
    """Embedding providers."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


class VectorStore(StrEnum):
    """Supported vector databases."""

    PINECONE = "pinecone"
    CHROMA = "chroma"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    PGVECTOR = "pgvector"


class LLMProvider(StrEnum):
    """Supported LLM providers."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    GROQ = "groq"


class AuthenticationType(StrEnum):
    """Authentication mechanisms."""

    NONE = "none"
    API_KEY = "api_key"
    BASIC = "basic"
    BEARER = "bearer"
    OAUTH2 = "oauth2"


class ContentType(StrEnum):
    """Supported document types."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    JSON = "json"
    CSV = "csv"


class EventType(StrEnum):
    """Platform event categories."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(StrEnum):
    """Severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExitCode(IntEnum):
    """Application exit codes."""

    SUCCESS = 0
    FAILURE = 1
    CONFIGURATION_ERROR = 2
    STARTUP_ERROR = 3
    SHUTDOWN_ERROR = 4


class FeatureFlag(StrEnum):
    """Platform feature flags."""

    RAG = "rag"
    TELEMETRY = "telemetry"
    AUDIT = "audit"
    CACHE = "cache"
    AUTHENTICATION = "authentication"


class CacheStrategy(StrEnum):
    """Caching strategies."""

    NONE = "none"
    MEMORY = "memory"
    REDIS = "redis"


class LifecycleState(Enum):
    """
    Internal lifecycle state.

    Uses auto() because values are never serialized outside the application.
    """

    CREATED = auto()
    INITIALIZED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()


__all__ = [
    "AuthenticationType",
    "CacheStrategy",
    "ChunkStatus",
    "ContentType",
    "DocumentStatus",
    "EmbeddingProvider",
    "Environment",
    "EventType",
    "ExitCode",
    "FeatureFlag",
    "HealthStatus",
    "HttpMethod",
    "LLMProvider",
    "LifecycleState",
    "LogLevel",
    "ResponseStatus",
    "Severity",
    "SortDirection",
    "TaskStatus",
    "VectorStore",
]
