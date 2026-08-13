"""
Tests for the standard reranking result model.
"""

import pytest

from backend.reranking.models import RerankResult


def test_rerank_result_creation() -> None:
    """
    Verify that a reranking result can be created.
    """

    result = RerankResult(
        index=2,
        score=0.8734,
    )

    assert result.index == 2
    assert result.score == 0.8734


def test_rerank_result_is_immutable() -> None:
    """
    Verify that reranking results are immutable.
    """

    result = RerankResult(
        index=1,
        score=0.75,
    )

    with pytest.raises(AttributeError):
        result.index = 2  # type: ignore[misc]
