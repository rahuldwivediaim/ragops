"""
File:
    backend/main.py

Purpose:
    FastAPI application entry point for the RAG Framework.
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.api import api_router

app = FastAPI(
    title="RAG Framework API",
    description="Enterprise Retrieval-Augmented Generation (RAG) Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ----------------------------------------------------------------------
# Register API Routers
# ----------------------------------------------------------------------

app.include_router(api_router)


# ----------------------------------------------------------------------
# Health Check
# ----------------------------------------------------------------------


@app.get(
    "/health",
    tags=["Health"],
)
def health() -> dict[str, str]:
    """Application health endpoint."""

    return {
        "status": "UP",
        "application": "RAG Framework",
    }


# ----------------------------------------------------------------------
# Root
# ----------------------------------------------------------------------


@app.get(
    "/",
    tags=["Home"],
)
def home() -> dict[str, str]:
    """Application root."""

    return {
        "message": "Welcome to the RAG Framework API",
    }
