"""
Provider Capabilities.

Defines the capabilities supported by a provider.

Author: RAGOps
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    """
    Immutable provider capabilities.
    """

    supports_text: bool = True

    supports_tables: bool = False

    supports_images: bool = False

    supports_layout: bool = False

    supports_ocr: bool = False
