"""
Application-wide constants used by the domain models.

Only constants that are shared across multiple models should be defined here.
Avoid putting model-specific business rules in this module.
"""

from __future__ import annotations

# ============================================================================
# String Lengths
# ============================================================================

CODE_LENGTH = 100
NAME_LENGTH = 100
TITLE_LENGTH = 255
DESCRIPTION_LENGTH = 1000

FILE_NAME_LENGTH = 512
FILE_EXTENSION_LENGTH = 20
FILE_PATH_LENGTH = 1024
MIME_TYPE_LENGTH = 255

MODEL_NAME_LENGTH = 100
PROVIDER_NAME_LENGTH = 100
VERSION_LENGTH = 50

EMAIL_LENGTH = 255
PHONE_LENGTH = 30
URL_LENGTH = 2048
LANGUAGE_LENGTH = 10

HASH_LENGTH = 128
CHECKSUM_LENGTH = 128

VECTOR_ID_LENGTH = 255
EXTERNAL_ID_LENGTH = 255

CONTENT_TYPE_LENGTH = 100
CONTENT_ENCODING_LENGTH = 50

STATUS_LENGTH = 50
TYPE_LENGTH = 50

KEY_LENGTH = 255
VALUE_LENGTH = 2048

TAG_LENGTH = 100

# ============================================================================
# Numeric Defaults
# ============================================================================

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

DEFAULT_VECTOR_DIMENSION = 1536

MAX_RETRY_COUNT = 5
DEFAULT_BATCH_SIZE = 100

# ============================================================================
# Miscellaneous
# ============================================================================

DEFAULT_TIMEZONE = "UTC"

UNKNOWN = "UNKNOWN"
SYSTEM = "SYSTEM"
