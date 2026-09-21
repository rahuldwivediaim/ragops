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
from backend.api.tenant import router as tenant_router
from backend.api.domain import router as domain_router
from backend.api.vector_infrastructure import router as vector_infrastructure_router

api_router = APIRouter()

api_router.include_router(tenant_router)
api_router.include_router(knowledge_base_router)
api_router.include_router(document_upload_router)
api_router.include_router(domain_router)
api_router.include_router(vector_infrastructure_router)


__all__ = [
    "api_router",
]
