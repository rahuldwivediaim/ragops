"""
RAGOps Platform Version Information.

This module provides a single source of truth for the platform version and
build metadata. It is intentionally dependency-free so it can be imported by
any module without creating circular dependencies.

Author:
    RAGOps Development Team

License:
    MIT
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from os import getenv
from typing import Any

###############################################################################
# Platform Version
###############################################################################

VERSION = "0.1.0"
API_VERSION = "v1"

###############################################################################
# Build Metadata
###############################################################################

BUILD_NUMBER = getenv("RAGOPS_BUILD_NUMBER", "1")
BUILD_TIMESTAMP = getenv("RAGOPS_BUILD_TIMESTAMP")
GIT_COMMIT = getenv("RAGOPS_GIT_COMMIT")
ENVIRONMENT = getenv("RAGOPS_ENVIRONMENT", "development")


@dataclass(frozen=True, slots=True)
class VersionInfo:
    """
    Represents platform version metadata.

    Attributes:
        version:
            Semantic version of the platform.

        api_version:
            Current REST API version.

        build_number:
            CI/CD build number.

        build_timestamp:
            ISO-8601 timestamp of build.

        git_commit:
            Git commit hash.

        environment:
            Runtime environment.
    """

    version: str
    api_version: str
    build_number: str
    build_timestamp: str | None
    git_commit: str | None
    environment: str

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the version information into a dictionary.

        Returns:
            Dictionary representation.
        """
        return asdict(self)

    def to_json(self) -> dict[str, Any]:
        """
        Alias for JSON serialization compatibility.

        Returns:
            Serializable dictionary.
        """
        return self.to_dict()


_VERSION_INFO = VersionInfo(
    version=VERSION,
    api_version=API_VERSION,
    build_number=BUILD_NUMBER,
    build_timestamp=BUILD_TIMESTAMP,
    git_commit=GIT_COMMIT,
    environment=ENVIRONMENT,
)


def get_version() -> str:
    """
    Return the platform semantic version.

    Returns:
        Semantic version string.
    """
    return VERSION


def get_api_version() -> str:
    """
    Return the REST API version.

    Returns:
        API version.
    """
    return API_VERSION


def get_version_info() -> VersionInfo:
    """
    Return the immutable VersionInfo object.

    Returns:
        VersionInfo instance.
    """
    return _VERSION_INFO


def get_build_info() -> dict[str, Any]:
    """
    Return build metadata as a serializable dictionary.

    Returns:
        Dictionary containing build metadata.
    """
    return _VERSION_INFO.to_dict()


def is_development() -> bool:
    """
    Determine whether the current environment is development.

    Returns:
        True if running in development mode.
    """
    return ENVIRONMENT.lower() == "development"


def is_production() -> bool:
    """
    Determine whether the current environment is production.

    Returns:
        True if running in production mode.
    """
    return ENVIRONMENT.lower() == "production"


def get_startup_banner() -> str:
    """
    Build a startup banner suitable for logging.

    Returns:
        Multi-line startup banner.
    """
    timestamp = BUILD_TIMESTAMP or datetime.now(UTC).isoformat()

    return (
        "\n"
        "=============================================================\n"
        "                     RAGOps Platform\n"
        "=============================================================\n"
        f"Version        : {VERSION}\n"
        f"API Version    : {API_VERSION}\n"
        f"Environment    : {ENVIRONMENT}\n"
        f"Build Number   : {BUILD_NUMBER}\n"
        f"Git Commit     : {GIT_COMMIT or 'N/A'}\n"
        f"Build Time     : {timestamp}\n"
        "============================================================="
    )


__all__ = [
    "VERSION",
    "API_VERSION",
    "BUILD_NUMBER",
    "BUILD_TIMESTAMP",
    "GIT_COMMIT",
    "ENVIRONMENT",
    "VersionInfo",
    "get_version",
    "get_api_version",
    "get_version_info",
    "get_build_info",
    "get_startup_banner",
    "is_development",
    "is_production",
]
