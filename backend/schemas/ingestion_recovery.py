"""Schemas describing safe recovery options for an ingestion."""

from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.models.enums import IngestionStatus, PipelineStage


class RecoveryAction(str, Enum):
    """Recommended action for a failed ingestion."""

    RETRY_VALIDATION = "RETRY_VALIDATION"
    RETRY_EXTRACTION = "RETRY_EXTRACTION"
    RETRY_EMBEDDING = "RETRY_EMBEDDING"
    RETRY_FROM_EMBEDDING = "RETRY_FROM_EMBEDDING"
    FIX_DOCUMENT_AND_REPROCESS = "FIX_DOCUMENT_AND_REPROCESS"
    NONE = "NONE"


class IngestionRecoveryPlan(BaseModel):
    """Derived recovery plan for one ingestion execution."""

    model_config = ConfigDict(use_enum_values=True)

    ingestion_id: UUID
    ingestion_status: IngestionStatus
    failed_stage: PipelineStage | None = None
    last_executed_stage: PipelineStage | None = None
    last_durable_checkpoint: PipelineStage | None = None
    recovery_stage: PipelineStage | None = None
    retryable: bool
    requires_rebuild: bool
    requires_vector_reconciliation: bool
    recommended_action: RecoveryAction
    message: str
