"""
backend/common/config/logging.py

Logging configuration models for the RAGOps Platform.
"""

from __future__ import annotations

from pydantic import Field

from backend.common.enums import LogLevel

from .base import BaseConfig


class LogRotationConfig(BaseConfig):
    """Configuration for log file rotation."""

    enabled: bool = True
    max_file_size_mb: int = Field(default=100, ge=1)
    backup_count: int = Field(default=10, ge=1)
    compress: bool = True


class ConsoleLoggingConfig(BaseConfig):
    """Console logging configuration."""

    enabled: bool = True
    json_output: bool = False
    colored: bool = True


class FileLoggingConfig(BaseConfig):
    """File logging configuration."""

    enabled: bool = True
    directory: str = "logs"
    filename: str = "application.log"
    json_output: bool = True
    rotation: LogRotationConfig = Field(
        default_factory=LogRotationConfig,
    )


class AuditLoggingConfig(BaseConfig):
    """Audit logging configuration."""

    enabled: bool = True
    filename: str = "audit.log"


class LoggingConfig(BaseConfig):
    """Root logging configuration."""

    level: LogLevel = LogLevel.INFO

    service_name: str = "ragops"

    correlation_id_header: str = "X-Correlation-ID"
    request_id_header: str = "X-Request-ID"

    console: ConsoleLoggingConfig = Field(
        default_factory=ConsoleLoggingConfig,
    )

    file: FileLoggingConfig = Field(
        default_factory=FileLoggingConfig,
    )

    audit: AuditLoggingConfig = Field(
        default_factory=AuditLoggingConfig,
    )


__all__ = [
    "LogRotationConfig",
    "ConsoleLoggingConfig",
    "FileLoggingConfig",
    "AuditLoggingConfig",
    "LoggingConfig",
]
