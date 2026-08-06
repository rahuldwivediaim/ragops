"""
backend/common/config/base.py

Base configuration models shared across the RAGOps platform.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseConfig(BaseModel):
    """Base immutable configuration model."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )


class PathConfig(BaseConfig):
    """Application directory configuration."""

    root_dir: Path = Path(".")
    data_dir: Path = Path("data")
    logs_dir: Path = Path("logs")
    temp_dir: Path = Path("temp")

    def ensure_directories(self) -> None:
        for path in (self.data_dir, self.logs_dir, self.temp_dir):
            path.mkdir(parents=True, exist_ok=True)


class FeatureFlags(BaseConfig):
    rag: bool = True
    plugins: bool = True
    telemetry: bool = True
    caching: bool = True
    authentication: bool = True
    authorization: bool = True


class RetryPolicy(BaseConfig):
    max_attempts: int = Field(default=3, ge=1)
    initial_delay_seconds: float = Field(default=1.0, gt=0)
    max_delay_seconds: float = Field(default=30.0, gt=0)
    exponential_backoff: bool = True


class HealthCheckConfig(BaseConfig):
    enabled: bool = True
    timeout_seconds: int = Field(default=10, ge=1)


class NamedConfig(BaseConfig):
    name: str
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "BaseConfig",
    "FeatureFlags",
    "HealthCheckConfig",
    "NamedConfig",
    "PathConfig",
    "RetryPolicy",
]
