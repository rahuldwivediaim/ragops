"""
File:
    backend/api/__init__.py

Purpose:
    Central API router for the application.

Every feature router should be registered here.
"""

from fastapi import APIRouter

from backend.api.document_upload import router as document_upload_router
from backend.api.knowledge_base import router as knowledge_base_router

api_router = APIRouter()

api_router.include_router(knowledge_base_router)
api_router.include_router(document_upload_router)

__all__ = [
    "api_router",
]
