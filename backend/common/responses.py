"""
backend/common/responses.py

Generic API response models for the RAGOps platform.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .metadata import (
    PageMetadata,
    ResponseMetadata,
)

T = TypeVar("T")


class ApiError(BaseModel):
    """Represents a standard API error."""

    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    field: str | None = None


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response."""

    model_config = ConfigDict(extra="forbid")

    success: bool = True
    message: str | None = None
    data: T | None = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
    errors: list[ApiError] = Field(default_factory=list)

    @classmethod
    def success_response(
        cls,
        data: T | None = None,
        message: str | None = None,
    ) -> ApiResponse[T]:
        return cls(
            success=True,
            data=data,
            message=message,
        )

    @classmethod
    def error_response(
        cls,
        *,
        code: str,
        message: str,
        field: str | None = None,
    ) -> ApiResponse[T]:
        return cls(
            success=False,
            errors=[
                ApiError(
                    code=code,
                    message=message,
                    field=field,
                ),
            ],
        )


class PaginatedResponse(ApiResponse[list[T]], Generic[T]):
    """API response containing paginated data."""

    @classmethod
    def create(
        cls,
        *,
        items: list[T],
        metadata: ResponseMetadata,
        page: PageMetadata,
        message: str | None = None,
    ) -> PaginatedResponse[T]:
        metadata.page = page

        return cls(
            success=True,
            data=items,
            message=message,
            metadata=metadata,
        )


__all__ = [
    "ApiError",
    "ApiResponse",
    "PaginatedResponse",
]
