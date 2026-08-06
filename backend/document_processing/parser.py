"""
Document parser implementations.

Currently supports PDF documents.

The parser is intentionally responsible only for
extracting text from a document.
"""

from __future__ import annotations

from pathlib import Path

import fitz


class PdfParser:
    """
    Extract text from PDF documents.
    """

    def parse(
        self,
        source: str | Path,
    ) -> str:
        """
        Parse a PDF document.

        Parameters
        ----------
        source
            Path to the PDF.

        Returns
        -------
        str
            Extracted text.

        Raises
        ------
        FileNotFoundError
            If the document does not exist.

        ValueError
            If the path is not a PDF.

        RuntimeError
            If the PDF cannot be opened.
        """

        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(path)

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"{path} is not a PDF document.")

        try:
            document = fitz.open(path)

            pages: list[str] = []

            for page in document:
                pages.append(page.get_text())

            document.close()

            return "\n".join(pages).strip()

        except Exception as ex:
            raise RuntimeError(f"Unable to parse document '{path.name}'.") from ex


__all__ = [
    "PdfParser",
]
