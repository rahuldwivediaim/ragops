"""
SQLAlchemy declarative base for the RAG Framework.

This module defines the application's declarative base class and
centralizes metadata naming conventions for all database objects.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Consistent naming convention for all constraints and indexes.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for every SQLAlchemy model.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
