"""
File:
    backend/api/knowledge_base.py

Purpose:
    FastAPI router for Knowledge Base CRUD operations.
"""

from __future__ import annotations

from uuid import UUID
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
)
from backend.services.knowledge_base_service import (
    KnowledgeBaseService,
)

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"],
)


@router.post(
    "",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_base(
    request: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    """Create a Knowledge Base."""

    service = KnowledgeBaseService(db)

    try:
        return service.create(request)
    except ValueError as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ex),
        ) from ex


@router.get(
    "",
    response_model=list[KnowledgeBaseResponse],
)
def get_knowledge_bases(
    db: Session = Depends(get_db),
) -> Sequence[KnowledgeBaseResponse]:
    """Return all Knowledge Bases."""

    service = KnowledgeBaseService(db)
    return service.get_all()


@router.get(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
)
def get_knowledge_base(
    knowledge_base_id: UUID,
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    """Return a Knowledge Base by ID."""

    service = KnowledgeBaseService(db)

    try:
        return service.get_by_id(knowledge_base_id)
    except ValueError as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ex),
        ) from ex


@router.put(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
)
def update_knowledge_base(
    knowledge_base_id: UUID,
    request: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    """Update a Knowledge Base."""

    service = KnowledgeBaseService(db)

    try:
        return service.update(
            knowledge_base_id,
            request,
        )
    except ValueError as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ex),
        ) from ex


@router.delete(
    "/{knowledge_base_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_knowledge_base(
    knowledge_base_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """Delete a Knowledge Base."""

    service = KnowledgeBaseService(db)

    try:
        service.delete(knowledge_base_id)
    except ValueError as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ex),
        ) from ex
