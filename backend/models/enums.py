"""
Shared enumerations for the RAG Framework domain models.

All SQLAlchemy models, Pydantic schemas, services and APIs should
reuse these enums instead of creating duplicate string constants.
"""

from __future__ import annotations

from enum import Enum


# ============================================================================
# Knowledge Base
# ============================================================================


class KnowledgeBaseStatus(str, Enum):
    """Knowledge Base lifecycle."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


# ============================================================================
# Document
# ============================================================================


class DocumentStatus(str, Enum):
    """Document lifecycle."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class DocumentType(str, Enum):
    """Supported document types."""

    PDF = "PDF"
    DOCX = "DOCX"
    DOC = "DOC"
    TXT = "TXT"
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"
    CSV = "CSV"
    XLSX = "XLSX"
    PPTX = "PPTX"
    JSON = "JSON"
    XML = "XML"
    IMAGE = "IMAGE"
    OTHER = "OTHER"


class DocumentSource(str, Enum):
    """Document source."""

    LOCAL = "LOCAL"
    URL = "URL"
    API = "API"
    SHAREPOINT = "SHAREPOINT"
    S3 = "S3"
    AZURE_BLOB = "AZURE_BLOB"
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    MANUAL = "MANUAL"


# ============================================================================
# Ingestion Pipeline
# ============================================================================


class IngestionStatus(str, Enum):
    """Overall ingestion status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PipelineStage(str, Enum):
    """Pipeline execution stage."""

    UPLOAD = "UPLOAD"
    VALIDATION = "VALIDATION"
    EXTRACTION = "EXTRACTION"
    CLEANING = "CLEANING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXING = "INDEXING"
    COMPLETED = "COMPLETED"


class ProcessingJobStatus(str, Enum):
    """Processing job status."""

    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# ============================================================================
# Embedding / Vector
# ============================================================================


class EmbeddingProvider(str, Enum):
    """Embedding model provider."""

    OPENAI = "OPENAI"
    AZURE_OPENAI = "AZURE_OPENAI"
    OLLAMA = "OLLAMA"
    HUGGINGFACE = "HUGGINGFACE"
    COHERE = "COHERE"
    VOYAGE_AI = "VOYAGE_AI"
    GOOGLE = "GOOGLE"


class VectorProvider(str, Enum):
    """Vector database provider."""

    PINECONE = "PINECONE"
    PGVECTOR = "PGVECTOR"
    WEAVIATE = "WEAVIATE"
    QDRANT = "QDRANT"
    CHROMA = "CHROMA"
    MILVUS = "MILVUS"


class StorageProvider(str, Enum):
    """Binary storage provider."""

    LOCAL = "LOCAL"
    AWS_S3 = "AWS_S3"
    AZURE_BLOB = "AZURE_BLOB"
    GOOGLE_CLOUD_STORAGE = "GOOGLE_CLOUD_STORAGE"


# ============================================================================
# Metadata
# ============================================================================


class MetadataDataType(str, Enum):
    """Supported metadata value types."""

    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    JSON = "JSON"


# ============================================================================
# Audit
# ============================================================================


class AuditAction(str, Enum):
    """Audit log actions."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    RESTORE = "RESTORE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXECUTE = "EXECUTE"


# ============================================================================
# Common
# ============================================================================


class Priority(str, Enum):
    """Execution priority."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TriggerType(str, Enum):
    """Pipeline trigger source."""

    MANUAL = "MANUAL"
    API = "API"
    SCHEDULED = "SCHEDULED"
    EVENT = "EVENT"


class ConfigurationScope(str, Enum):
    """Configuration scope."""

    SYSTEM = "SYSTEM"
    TENANT = "TENANT"
    USER = "USER"
