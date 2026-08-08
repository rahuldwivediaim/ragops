"""
Document Processing Enums.

Enumerations used by the document processing subsystem.

Author: RAGOps
"""

from __future__ import annotations

from enum import StrEnum


class DocumentFormat(StrEnum):
    """
    Supported document formats.
    """

    PDF = "PDF"

    DOCX = "DOCX"

    TXT = "TXT"

    MARKDOWN = "MARKDOWN"

    HTML = "HTML"

    CSV = "CSV"

    XLSX = "XLSX"

    PPTX = "PPTX"

    JSON = "JSON"

    XML = "XML"

    UNKNOWN = "UNKNOWN"


__all__ = [
    "DocumentFormat",
]
