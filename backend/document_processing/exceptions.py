"""
Document Processing Exceptions.

Defines the exception hierarchy used by the document
processing subsystem.

Author: RAGOps
"""

from __future__ import annotations


class DocumentProcessingError(Exception):
    """
    Base exception for document processing.
    """


class ParserError(DocumentProcessingError):
    """
    Base parser exception.
    """


class UnsupportedDocumentError(ParserError):
    """
    Raised when no parser exists for a document.
    """


class DocumentReadError(ParserError):
    """
    Raised when a document cannot be read.
    """


class DocumentCorruptedError(ParserError):
    """
    Raised when a document is corrupted.
    """


class EncryptedDocumentError(ParserError):
    """
    Raised when a document is encrypted.
    """


class ParserConfigurationError(ParserError):
    """
    Raised when a parser has been configured incorrectly.
    """


class ParserRegistrationError(ParserError):
    """
    Raised when parser registration fails.
    """


__all__ = [
    "DocumentProcessingError",
    "ParserError",
    "UnsupportedDocumentError",
    "DocumentReadError",
    "DocumentCorruptedError",
    "EncryptedDocumentError",
    "ParserConfigurationError",
    "ParserRegistrationError",
]
