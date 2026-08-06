"""
File:
    backend/common/utils/upload_file_helper.py

Purpose:
    Utility for working with FastAPI UploadFile objects.

Description:
    Converts uploaded files into temporary files that can be
    consumed by the storage layer.

Responsibilities:
    - Persist UploadFile to a temporary location.
    - Return the temporary file path.
    - Clean up temporary files.

Does NOT:
    - Perform validation.
    - Access storage providers.
    - Access the database.
    - Compute hashes.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import UploadFile


class UploadFileHelper:
    """
    Helper methods for FastAPI UploadFile.
    """

    @staticmethod
    def save_to_temp(
        upload_file: UploadFile,
    ) -> Path:
        """
        Save an uploaded file to a temporary location.

        Parameters
        ----------
        upload_file:
            FastAPI UploadFile instance.

        Returns
        -------
        Path
            Path to the temporary file.
        """

        suffix = Path(upload_file.filename or "").suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            upload_file.file.seek(0)
            shutil.copyfileobj(upload_file.file, temp_file)

            return Path(temp_file.name)

    @staticmethod
    def cleanup(
        file_path: Path,
    ) -> None:
        """
        Delete a temporary file.

        Parameters
        ----------
        file_path:
            Temporary file path.
        """

        try:
            file_path.unlink(missing_ok=True)
        except Exception:
            # Cleanup should never interrupt business logic.
            pass


__all__ = [
    "UploadFileHelper",
]
