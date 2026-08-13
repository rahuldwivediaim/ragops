"""
Unit tests for Retriever.

These tests verify Retriever orchestration without making
real OpenAI or Pinecone calls.

The real Pinecone integration remains covered separately by:

    test_retriever_pinecone.py
"""

from __future__ import annotations

from typing import Any

import pytest

from backend.embeddings.models.embedding_result import (
    EmbeddingResult,
)
from backend.embeddings.providers.base_embedding_provider import (
    BaseEmbeddingProvider,
)
from backend.reranking.models import RerankResult
from backend.reranking.providers.base_reranker import (
    BaseReranker,
)
from backend.retrieval.retriever import Retriever
from backend.vector_store.providers.base_vector_store import (
    BaseVectorStore,
)


class FakeEmbeddingProvider(BaseEmbeddingProvider):
    """Fake embedding provider for Retriever unit tests."""

    def __init__(self) -> None:
        self.last_text: str | None = None

    @property
    def provider_name(self) -> str:
        return "fake"

    @property
    def model_name(self) -> str:
        return "fake-embedding"

    @property
    def dimensions(self) -> int:
        return 3

    def embed(
        self,
        text: str,
    ) -> EmbeddingResult:
        self.last_text = text

        return EmbeddingResult(
            vector=[
                0.1,
                0.2,
                0.3,
            ],
            provider=self.provider_name,
            model_name=self.model_name,
            dimensions=self.dimensions,
            embedding_version=1,
        )


class FakeVectorStore(BaseVectorStore):
    """Fake vector store for Retriever unit tests."""

    def __init__(
        self,
        results: list[dict[str, Any]],
    ) -> None:
        self.results = results
        self.last_vector: list[float] | None = None
        self.last_top_k: int | None = None
        self.last_metadata_filter: dict[str, Any] | None = None

    @property
    def provider_name(self) -> str:
        return "fake"

    def upsert(
        self,
        vector_id: str,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Insert or update a fake vector."""

    def delete(
        self,
        vector_ids: list[str],
    ) -> None:
        """Delete fake vectors."""

    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        self.last_vector = vector
        self.last_top_k = top_k
        self.last_metadata_filter = metadata_filter

        return self.results

    def count(self) -> int:
        return len(self.results)


class FakeReranker(BaseReranker):
    """Fake reranker for Retriever unit tests."""

    def __init__(
        self,
        rerank_order: list[int],
    ) -> None:
        self.rerank_order = rerank_order
        self.last_query: str | None = None
        self.last_documents: list[str] | None = None
        self.last_top_k: int | None = None

    @property
    def provider_name(self) -> str:
        return "fake"

    @property
    def model_name(self) -> str:
        return "fake-reranker"

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[RerankResult]:
        self.last_query = query
        self.last_documents = documents
        self.last_top_k = top_k

        results = [
            RerankResult(
                index=index,
                score=float(len(self.rerank_order) - position),
            )
            for position, index in enumerate(self.rerank_order)
        ]

        return results

    def close(self) -> None:
        """Close the fake reranker."""


def _result(
    vector_id: str,
    score: float,
    text: str,
) -> dict[str, Any]:
    """Build a standard fake vector-store result."""

    return {
        "vector_id": vector_id,
        "score": score,
        "metadata": {
            "document_id": "document-001",
            "document_version_id": "version-001",
            "chunk_id": vector_id,
            "chunk_number": 1,
            "filename": "sample.txt",
            "text": text,
        },
    }


def test_retriever_without_reranker_preserves_vector_store_order() -> None:
    """Retriever should preserve vector-store order without reranking."""

    embedding_provider = FakeEmbeddingProvider()

    vector_store = FakeVectorStore(
        results=[
            _result(
                "chunk-001",
                0.90,
                "Annual leave policy.",
            ),
            _result(
                "chunk-002",
                0.80,
                "Work from home policy.",
            ),
            _result(
                "chunk-003",
                0.70,
                "Incident reporting policy.",
            ),
        ]
    )

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    results = retriever.retrieve(
        query="What is the leave policy?",
        top_k=3,
    )

    assert [result["vector_id"] for result in results] == [
        "chunk-001",
        "chunk-002",
        "chunk-003",
    ]

    assert embedding_provider.last_text == ("What is the leave policy?")

    assert vector_store.last_vector == [
        0.1,
        0.2,
        0.3,
    ]

    assert vector_store.last_top_k == 3


def test_retriever_with_reranker_reorders_results() -> None:
    """Retriever should return results in reranker order."""

    embedding_provider = FakeEmbeddingProvider()

    vector_store = FakeVectorStore(
        results=[
            _result(
                "chunk-001",
                0.90,
                "Annual leave policy.",
            ),
            _result(
                "chunk-002",
                0.80,
                "Work from home policy.",
            ),
            _result(
                "chunk-003",
                0.70,
                "Incident reporting policy.",
            ),
        ]
    )

    reranker = FakeReranker(
        rerank_order=[
            1,
            2,
            0,
        ]
    )

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        reranker=reranker,
    )

    results = retriever.retrieve(
        query="What is the work from home policy?",
        top_k=3,
    )

    assert [result["vector_id"] for result in results] == [
        "chunk-002",
        "chunk-003",
        "chunk-001",
    ]


def test_retriever_passes_query_and_text_to_reranker() -> None:
    """Retriever should pass query and chunk text to reranker."""

    embedding_provider = FakeEmbeddingProvider()

    vector_store = FakeVectorStore(
        results=[
            _result(
                "chunk-001",
                0.90,
                "Annual leave policy.",
            ),
            _result(
                "chunk-002",
                0.80,
                "Work from home policy.",
            ),
        ]
    )

    reranker = FakeReranker(
        rerank_order=[
            1,
            0,
        ]
    )

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        reranker=reranker,
    )

    query = "What is the work from home policy?"

    retriever.retrieve(
        query=query,
        top_k=2,
    )

    assert reranker.last_query == query

    assert reranker.last_documents == [
        "Annual leave policy.",
        "Work from home policy.",
    ]

    assert reranker.last_top_k == 2


def test_retriever_returns_empty_list_when_vector_store_returns_empty() -> None:
    """Retriever should return empty list when no candidates exist."""

    embedding_provider = FakeEmbeddingProvider()

    vector_store = FakeVectorStore(results=[])

    reranker = FakeReranker(rerank_order=[])

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        reranker=reranker,
    )

    results = retriever.retrieve(
        query="What is the leave policy?",
        top_k=5,
    )

    assert results == []

    assert reranker.last_query is None
    assert reranker.last_documents is None


def test_retriever_rejects_missing_chunk_text() -> None:
    """Retriever should reject candidates without text metadata."""

    embedding_provider = FakeEmbeddingProvider()

    vector_store = FakeVectorStore(
        results=[
            {
                "vector_id": "chunk-001",
                "score": 0.90,
                "metadata": {
                    "document_id": "document-001",
                    "document_version_id": "version-001",
                    "chunk_id": "chunk-001",
                    "chunk_number": 1,
                    "filename": "sample.txt",
                },
            }
        ]
    )

    reranker = FakeReranker(
        rerank_order=[
            0,
        ]
    )

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        reranker=reranker,
    )

    with pytest.raises(
        ValueError,
        match="does not contain valid text metadata",
    ):
        retriever.retrieve(
            query="What is the leave policy?",
            top_k=1,
        )


def test_retriever_rejects_empty_query() -> None:
    """Retriever should reject an empty query."""

    embedding_provider = FakeEmbeddingProvider()

    vector_store = FakeVectorStore(results=[])

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    with pytest.raises(
        ValueError,
        match="Query cannot be empty",
    ):
        retriever.retrieve(
            query="   ",
            top_k=5,
        )


def test_retriever_rejects_invalid_top_k() -> None:
    """Retriever should reject zero or negative top_k."""

    embedding_provider = FakeEmbeddingProvider()

    vector_store = FakeVectorStore(results=[])

    retriever = Retriever(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    with pytest.raises(
        ValueError,
        match="top_k must be greater than zero",
    ):
        retriever.retrieve(
            query="What is the leave policy?",
            top_k=0,
        )
