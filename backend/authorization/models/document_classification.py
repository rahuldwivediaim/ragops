"""
Document classification model.

Defines the sensitivity classification applied to documents
and propagated to every vector chunk.
"""

from __future__ import annotations

from enum import StrEnum


class DocumentClassification(StrEnum):
    """
    Document sensitivity classification.

    Classification describes the sensitivity/governance level
    of a document. It does not itself grant or deny access.

    Authorization is determined by access policies.
    """

    PUBLIC = "public"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


__all__ = ["DocumentClassification"]
