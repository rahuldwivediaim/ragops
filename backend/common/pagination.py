"""
backend/common/pagination.py

Reusable pagination models for the RAGOps platform.
"""

from __future__ import annotations

from math import ceil

from pydantic import BaseModel, ConfigDict, Field


class PaginationRequest(BaseModel):
    """Pagination request parameters."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=1000)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginationInfo(BaseModel):
    """Pagination result information."""

    model_config = ConfigDict(extra="forbid")

    page: int
    page_size: int
    total_records: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(
        cls,
        *,
        page: int,
        page_size: int,
        total_records: int,
    ) -> PaginationInfo:
        total_pages = max(1, ceil(total_records / page_size)) if page_size else 1
        return cls(
            page=page,
            page_size=page_size,
            total_records=total_records,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )


__all__ = [
    "PaginationRequest",
    "PaginationInfo",
]
