"""
File:
    backend/common/utils/file_name.py

Purpose:
    Utility functions for working with file names.

Description:
    Provides reusable helper functions for normalizing file names,
    extracting file information, and generating versioned file names.

Responsibilities:
    - Normalize file names.
    - Extract file stem and extension.
    - Build versioned file names.

Does NOT:
    - Access the database.
    - Access the filesystem.
    - Perform logging.
    - Use application settings.
"""

from __future__ import annotations

import re
from pathlib import Path


_INVALID_CHARACTERS = re.compile(r"[^a-zA-Z0-9_-]+")


def get_extension(file_name: str) -> str:
    """
    Return the lowercase file extension without the leading dot.

    Example
    -------
    employee.pdf -> pdf
    """

    return Path(file_name).suffix.lower().lstrip(".")


def get_stem(file_name: str) -> str:
    """
    Return the filename without the extension.

    Example
    -------
    employee.pdf -> employee
    """

    return Path(file_name).stem


def normalize_filename(file_name: str) -> str:
    """
    Normalize a filename.

    Rules
    -----
    - lowercase
    - spaces become underscores
    - remove unsupported characters
    - collapse multiple underscores
    - preserve extension

    Examples
    --------
    Employee Handbook (Final).PDF
        ->
    employee_handbook_final.pdf
    """

    extension = get_extension(file_name)

    stem = get_stem(file_name).lower()

    stem = stem.replace(" ", "_")

    stem = _INVALID_CHARACTERS.sub("_", stem)

    stem = re.sub(r"_+", "_", stem)

    stem = stem.strip("_")

    if extension:
        return f"{stem}.{extension}"

    return stem


def build_versioned_filename(
    file_name: str,
    version_number: int,
) -> str:
    """
    Build a versioned filename.

    Examples
    --------
    employee.pdf
        ->
    employee_v001.pdf

    employee.pdf, version 27
        ->
    employee_v027.pdf
    """

    normalized = normalize_filename(file_name)

    extension = get_extension(normalized)

    stem = get_stem(normalized)

    version = f"v{version_number:03d}"

    if extension:
        return f"{stem}_{version}.{extension}"

    return f"{stem}_{version}"
