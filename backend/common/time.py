"""
backend/common/time.py

Enterprise UTC date/time utilities.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


def utc_today():
    """Return current UTC date."""
    return utc_now().date()


def utc_iso() -> str:
    """Return current UTC time as ISO-8601 string."""
    return utc_now().isoformat()


def to_iso(value: datetime) -> str:
    """Convert datetime to ISO-8601."""
    return value.astimezone(UTC).isoformat()


def from_iso(value: str) -> datetime:
    """Parse ISO-8601 datetime."""
    return datetime.fromisoformat(value)


def unix_timestamp(value: datetime | None = None) -> int:
    """Return Unix timestamp."""
    return int((value or utc_now()).timestamp())


def add_seconds(value: datetime, seconds: int) -> datetime:
    return value + timedelta(seconds=seconds)


def add_minutes(value: datetime, minutes: int) -> datetime:
    return value + timedelta(minutes=minutes)


def add_hours(value: datetime, hours: int) -> datetime:
    return value + timedelta(hours=hours)


def add_days(value: datetime, days: int) -> datetime:
    return value + timedelta(days=days)


def elapsed_milliseconds(start: datetime, end: datetime | None = None) -> float:
    end = end or utc_now()
    return (end - start).total_seconds() * 1000.0


def elapsed_seconds(start: datetime, end: datetime | None = None) -> float:
    end = end or utc_now()
    return (end - start).total_seconds()


def is_expired(expiry: datetime) -> bool:
    return utc_now() >= expiry


def seconds_until(expiry: datetime) -> int:
    return max(0, int((expiry - utc_now()).total_seconds()))


__all__ = [
    "utc_now",
    "utc_today",
    "utc_iso",
    "to_iso",
    "from_iso",
    "unix_timestamp",
    "add_seconds",
    "add_minutes",
    "add_hours",
    "add_days",
    "elapsed_milliseconds",
    "elapsed_seconds",
    "is_expired",
    "seconds_until",
]
