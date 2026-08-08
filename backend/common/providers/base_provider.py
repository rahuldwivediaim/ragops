"""
Base Provider.

Defines the common contract implemented by all providers
used within RAGOps.

Author: RAGOps
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.common.providers.provider_capabilities import (
    ProviderCapabilities,
)
from backend.common.providers.provider_info import (
    ProviderInfo,
)


class BaseProvider(ABC):
    """
    Abstract base class for all providers.
    """

    @property
    @abstractmethod
    def info(
        self,
    ) -> ProviderInfo:
        """
        Provider metadata.
        """

    @property
    @abstractmethod
    def capabilities(
        self,
    ) -> ProviderCapabilities:
        """
        Provider capabilities.
        """
