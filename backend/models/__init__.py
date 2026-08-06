"""
RAG Framework SQLAlchemy Models.

This package exposes all ORM models so that SQLAlchemy can
configure relationships correctly.
"""

from __future__ import annotations

# ruff: noqa: F403

# ----------------------------------------------------------------------
# Foundation
# ----------------------------------------------------------------------

from .base import Base
from .constants import *
from .entity import Entity
from .enums import *
from .mixins import (
    CodeMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)

# ----------------------------------------------------------------------
# Business Models
# ----------------------------------------------------------------------

from .knowledge_base import KnowledgeBase
from .document import Document
from .document_version import DocumentVersion
from .chunk import Chunk
from .embedding_profile import EmbeddingProfile
from .embedding import Embedding
from .ingestion import Ingestion
from .pipeline_event import PipelineEvent
from .processing_job import ProcessingJob
from .vector_index import VectorIndex

__all__ = [
    "Base",
    "Entity",
    "UUIDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "CodeMixin",
    "KnowledgeBase",
    "Document",
    "DocumentVersion",
    "Chunk",
    "EmbeddingProfile",
    "Embedding",
    "Ingestion",
    "PipelineEvent",
    "ProcessingJob",
    "VectorIndex",
]
