"""
Standard reranking result model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RerankResult:
    """
    Standard result returned by a reranker provider.
    """

    index: int
    score: float


__all__ = [
    "RerankResult",
]
