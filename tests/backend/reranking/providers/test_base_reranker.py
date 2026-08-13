"""
Tests for the base reranker contract.
"""

from backend.reranking.models import RerankResult
from backend.reranking.providers import BaseReranker


class FakeReranker(BaseReranker):
    """
    Test implementation of the BaseReranker contract.
    """

    @property
    def provider_name(self) -> str:
        return "fake"

    @property
    def model_name(self) -> str:
        return "fake-reranker-v1"

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[RerankResult]:
        results = [
            RerankResult(
                index=index,
                score=float(len(document)),
            )
            for index, document in enumerate(documents)
        ]

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        if top_k is not None:
            return results[:top_k]

        return results


def test_fake_reranker_implements_contract() -> None:
    """
    Verify the base reranker contract.
    """

    reranker = FakeReranker()

    assert reranker.provider_name == "fake"
    assert reranker.model_name == "fake-reranker-v1"


def test_rerank_returns_results() -> None:
    """
    Verify that reranking returns framework-standard results.
    """

    reranker = FakeReranker()

    documents = [
        "Short document.",
        "This is a considerably longer document.",
        "Medium document here.",
    ]

    results = reranker.rerank(
        query="test query",
        documents=documents,
    )

    assert len(results) == 3
    assert all(isinstance(result, RerankResult) for result in results)


def test_rerank_orders_by_score() -> None:
    """
    Verify that results are returned in descending score order.
    """

    reranker = FakeReranker()

    documents = [
        "A",
        "A much longer document",
        "Medium",
    ]

    results = reranker.rerank(
        query="test query",
        documents=documents,
    )

    assert results[0].index == 1
    assert results[0].score >= results[1].score
    assert results[1].score >= results[2].score


def test_rerank_respects_top_k() -> None:
    """
    Verify that top_k limits the number of results.
    """

    reranker = FakeReranker()

    documents = [
        "Document one",
        "Document two",
        "Document three",
        "Document four",
    ]

    results = reranker.rerank(
        query="test query",
        documents=documents,
        top_k=2,
    )

    assert len(results) == 2


def test_close_has_default_implementation() -> None:
    """
    Verify that providers can use the default close implementation.
    """

    reranker = FakeReranker()

    reranker.close()
