"""
Database base.

Re-export the application's declarative Base so the entire project
uses a single SQLAlchemy metadata object.
"""

from backend.models.base import Base

__all__ = ["Base"]
