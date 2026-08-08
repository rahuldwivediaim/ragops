"""
Provider Information.

Immutable metadata describing a provider.

Author: RAGOps
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderInfo:
    """
    Immutable provider metadata.
    """

    name: str

    version: str

    vendor: str

    description: str

    homepage: str | None = None

    license_name: str | None = None
