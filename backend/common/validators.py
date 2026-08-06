"""
backend/common/validators.py

Reusable validation helpers for the RAGOps platform.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_FILENAME_RE = re.compile(r'^[^<>:"/\\|?*\x00-\x1F]+$')


def is_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def is_email(value: str) -> bool:
    return bool(_EMAIL_RE.fullmatch(value))


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def is_safe_filename(filename: str) -> bool:
    return bool(_FILENAME_RE.fullmatch(filename))


def validate_extension(filename: str, allowed: set[str]) -> bool:
    return Path(filename).suffix.lower() in {e.lower() for e in allowed}


def is_non_empty(value: str | None) -> bool:
    return bool(value and value.strip())


def is_positive_int(value: int) -> bool:
    return value > 0


def in_range(value: int | float, minimum: int | float, maximum: int | float) -> bool:
    return minimum <= value <= maximum


__all__ = [
    "is_uuid",
    "is_email",
    "is_url",
    "is_safe_filename",
    "validate_extension",
    "is_non_empty",
    "is_positive_int",
    "in_range",
]
