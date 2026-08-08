"""
PyMuPDF Provider.

PDF provider implementation using the PyMuPDF library.

Author: RAGOps
"""

from __future__ import annotations

from pathlib import Path

import fitz  # type: ignore[import-untyped]

from backend.common.providers import (
    ProviderCapabilities,
    ProviderInfo,
)
from backend.document_processing.enums import (
    DocumentFormat,
)
from backend.document_processing.models.parsed_document import (
    ParsedDocument,
)
from backend.document_processing.models.parsed_page import (
    ParsedPage,
)
from backend.document_processing.providers.pdf.base_pdf_provider import (
    BasePdfProvider,
)


class PyMuPDFProvider(BasePdfProvider):
    """
    PDF provider implementation using PyMuPDF.
    """

    @property
    def info(self) -> ProviderInfo:
        """
        Provider metadata.
        """
        return ProviderInfo(
            name="PyMuPDF",
            version=fitz.VersionBind,
            vendor="Artifex Software",
            description="PDF parser based on the PyMuPDF library.",
            homepage="https://pymupdf.readthedocs.io/",
            license_name="AGPL-3.0",
        )

    @property
    def capabilities(
        self,
    ) -> ProviderCapabilities:
        """
        Provider capabilities.
        """
        return ProviderCapabilities(
            supports_text=True,
            supports_tables=False,
            supports_images=True,
            supports_layout=True,
            supports_ocr=False,
        )

    def parse(
        self,
        file_path: Path,
    ) -> ParsedDocument:
        """
        Parse a PDF document.
        """

        with fitz.open(file_path) as pdf:
            document = ParsedDocument(
                filename=file_path.name,
                document_type=DocumentFormat.PDF,
                page_count=pdf.page_count,
            )

            for index, pdf_page in enumerate(pdf):
                page = ParsedPage(
                    page_number=index + 1,
                    text=pdf_page.get_text(),
                )

                document.add_page(page)

        return document
