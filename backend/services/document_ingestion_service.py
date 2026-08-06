"""
Document ingestion service.

This service orchestrates the complete document ingestion workflow.

Workflow
--------
1. Validate input
2. Parse document
3. Chunk text
4. Generate embeddings
5. Store vectors

Each step is intentionally isolated to make the pipeline
easy to extend and test.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.operations.enums import OperationType
from backend.operations.tracker import OperationTracker


class DocumentIngestionService:
    """
    Orchestrates document ingestion.
    """

    def __init__(
        self,
        tracker: OperationTracker,
    ) -> None:
        self._tracker = tracker

    def ingest(
        self,
        source: str | Path,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Ingest a document.

        Parameters
        ----------
        source
            Document path.

        metadata
            Optional document metadata.
        """

        path = Path(source)

        context = self._tracker.start(
            operation_type=OperationType.DOCUMENT_INGESTION,
            resource_name=path.name,
        )

        context.metadata.update(metadata or {})

        try:
            self._validate(path)

            document = self._parse(path)

            chunks = self._chunk(document)

            embeddings = self._embed(chunks)

            self._store(embeddings)

            self._tracker.complete(context)

        except Exception as ex:
            self._tracker.fail(
                context=context,
                exception=ex,
            )

            raise

    def _validate(
        self,
        path: Path,
    ) -> None:
        """
        Validate document.
        """

        if not path.exists():
            raise FileNotFoundError(path)

        if not path.is_file():
            raise ValueError(f"{path} is not a file.")

    def _parse(
        self,
        path: Path,
    ) -> str:
        """
        Parse document.

        Placeholder implementation.
        """

        raise NotImplementedError("PDF parser not implemented.")

    def _chunk(
        self,
        document: str,
    ) -> list[str]:
        """
        Chunk document.

        Placeholder implementation.
        """

        raise NotImplementedError("Chunker not implemented.")

    def _embed(
        self,
        chunks: list[str],
    ) -> list[Any]:
        """
        Generate embeddings.

        Placeholder implementation.
        """

        raise NotImplementedError("Embedding provider not implemented.")

    def _store(
        self,
        embeddings: list[Any],
    ) -> None:
        """
        Store embeddings.

        Placeholder implementation.
        """

        raise NotImplementedError("Vector store not implemented.")


__all__ = [
    "DocumentIngestionService",
]
