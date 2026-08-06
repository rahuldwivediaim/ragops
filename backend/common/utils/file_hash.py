"""
File:
    backend/common/utils/file_hash.py

Purpose:
    Utility functions for generating file hashes.

Description:
    Provides reusable helpers for generating SHA-256 hashes for files.

Responsibilities:
    - Compute SHA-256 hash.
    - Read files efficiently using streaming.

Does NOT:
    - Access the database.
    - Perform validation.
    - Store files.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class FileHash:
    """
    Utility class for file hashing.
    """

    DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1 MB

    @staticmethod
    def sha256(
        file_path: Path,
        *,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> str:
        """
        Generate SHA-256 hash for a file.

        Parameters
        ----------
        file_path:
            File to hash.

        chunk_size:
            Number of bytes to read per iteration.

        Returns
        -------
        str
            SHA-256 hexadecimal digest.
        """

        hasher = hashlib.sha256()

        with file_path.open("rb") as file:
            while chunk := file.read(chunk_size):
                hasher.update(chunk)

        return hasher.hexdigest()


__all__ = [
    "FileHash",
]
