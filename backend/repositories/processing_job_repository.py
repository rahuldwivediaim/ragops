"""Repository for durable ingestion processing jobs."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.enums import PipelineStage, ProcessingJobStatus
from backend.models.processing_job import ProcessingJob
from backend.repositories.base_repository import BaseRepository


class ProcessingJobRepository(BaseRepository[ProcessingJob]):
    """Persistence operations for processing-stage execution state."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, ProcessingJob)
        self._session = session

    def get_by_ingestion_and_stage(
        self, *, ingestion_id: UUID, stage: PipelineStage
    ) -> ProcessingJob | None:
        statement = select(ProcessingJob).where(
            ProcessingJob.ingestion_id == ingestion_id,
            ProcessingJob.stage == stage,
        )
        return self._session.scalar(statement)

    def list_by_ingestion(self, *, ingestion_id: UUID) -> list[ProcessingJob]:
        """Return processing jobs for an ingestion in pipeline order."""
        statement = (
            select(ProcessingJob)
            .where(ProcessingJob.ingestion_id == ingestion_id)
            .order_by(ProcessingJob.sequence_number.asc(), ProcessingJob.created_at.asc())
        )
        return list(self._session.scalars(statement).all())

    def create_running(
        self, *, ingestion_id: UUID, stage: PipelineStage, sequence_number: int
    ) -> ProcessingJob:
        job = ProcessingJob(
            ingestion_id=ingestion_id,
            stage=stage,
            status=ProcessingJobStatus.RUNNING,
            sequence_number=sequence_number,
            retry_count=0,
            records_processed=0,
            error_message=None,
        )
        self._session.add(job)
        self._session.commit()
        self._session.refresh(job)
        return job

    def mark_running(self, job: ProcessingJob) -> ProcessingJob:
        job.status = ProcessingJobStatus.RUNNING
        job.error_message = None
        job.duration_ms = None
        job.records_processed = 0
        job.retry_count += 1
        self._session.commit()
        self._session.refresh(job)
        return job

    def mark_completed(
        self, job: ProcessingJob, *, duration_ms: int, records_processed: int
    ) -> ProcessingJob:
        job.status = ProcessingJobStatus.COMPLETED
        job.duration_ms = max(duration_ms, 0)
        job.records_processed = max(records_processed, 0)
        job.error_message = None
        self._session.commit()
        self._session.refresh(job)
        return job

    def mark_failed(
        self, job: ProcessingJob, *, duration_ms: int, exception: Exception
    ) -> ProcessingJob:
        job.status = ProcessingJobStatus.FAILED
        job.duration_ms = max(duration_ms, 0)
        job.error_message = str(exception)
        self._session.commit()
        self._session.refresh(job)
        return job

    def close(self) -> None:
        self._session.close()
