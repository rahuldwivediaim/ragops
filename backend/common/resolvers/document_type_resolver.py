"""
File:
    backend/common/resolvers/document_type_resolver.py

Purpose:
    Resolve document types from file names.

Responsibilities:
    - Resolve DocumentType from file extension.
    - Validate supported document types.
    - Return supported extensions.

Future Enhancements:
    - MIME type lookup
    - Default parser lookup
    - Preview capability
    - OCR capability
"""

from __future__ import annotations

from pathlib import Path

from backend.models.enums import DocumentType


class DocumentTypeResolver:
    """
    Resolver responsible for document type mapping.
    """

    _TYPE_MAP: dict[str, DocumentType] = {
        ".pdf": DocumentType.PDF,
        ".docx": DocumentType.DOCX,
        ".txt": DocumentType.TXT,
        ".md": DocumentType.MARKDOWN,
        ".csv": DocumentType.CSV,
        ".xlsx": DocumentType.XLSX,
        ".pptx": DocumentType.PPTX,
    }

    @classmethod
    def resolve(
        cls,
        filename: str,
    ) -> DocumentType:
        """
        Resolve the DocumentType from a filename.

        Raises
        ------
        ValueError
            If the extension is not supported.
        """

        extension = Path(filename).suffix.lower()

        try:
            return cls._TYPE_MAP[extension]

        except KeyError as ex:
            raise ValueError(f"Unsupported document type '{extension}'.") from ex

    @classmethod
    def is_supported(
        cls,
        filename: str,
    ) -> bool:
        """
        Check whether a filename is supported.
        """

        extension = Path(filename).suffix.lower()

        return extension in cls._TYPE_MAP

    @classmethod
    def supported_extensions(
        cls,
    ) -> tuple[str, ...]:
        """
        Return all supported document extensions.
        """

        return tuple(sorted(cls._TYPE_MAP.keys()))
