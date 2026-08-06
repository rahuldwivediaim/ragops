"""
backend/common/logging/logger.py

Logging utilities for the RAGOps Platform.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGER_NAME = "ragops.operations"

_logger: logging.Logger | None = None


def get_operations_logger() -> logging.Logger:
    """
    Return the singleton operations logger.

    The logger writes business operation events to
    logs/operations.log.
    """

    global _logger

    if _logger is not None:
        return _logger

    log_directory = Path("logs")
    log_directory.mkdir(parents=True, exist_ok=True)

    log_file = log_directory / "operations.log"

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=100 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8",
        )

        formatter = logging.Formatter(
            fmt=("%(asctime)s | %(levelname)s | %(message)s"),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

    _logger = logger

    return logger


__all__ = [
    "get_operations_logger",
]
