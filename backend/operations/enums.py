"""
Enumerations for the Operations Framework.
"""

from enum import Enum


class OperationType(str, Enum):
    """
    Supported business operations.
    """

    DOCUMENT_INGESTION = "DOCUMENT_INGESTION"
    DOCUMENT_DELETION = "DOCUMENT_DELETION"
    DOCUMENT_UPDATE = "DOCUMENT_UPDATE"

    QUERY = "QUERY"

    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class OperationStatus(str, Enum):
    """
    Lifecycle status of an operation.
    """

    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class OperationProvider(str, Enum):
    """
    Supported operation providers.
    """

    CONSOLE = "CONSOLE"
    FILE = "FILE"
    DATABASE = "DATABASE"
