"""
Vector infrastructure setup API.

Provides the API used by the administration layer to configure the
physical vector infrastructure used by RAGOps.

The endpoint delegates all infrastructure lifecycle decisions to
VectorInfrastructureSetupService.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.common.dependency_injection.vector_infrastructure_dependencies import (
    VectorInfrastructureServiceDependency,
)
from backend.models.enums import StorageProvider
from backend.schemas.vector_infrastructure import (
    VectorInfrastructureSetupRequest,
    VectorInfrastructureSetupResponse,
)
from backend.vector_store.provisioning.models import VectorIndexSpec


router = APIRouter(
    prefix="/vector-infrastructure",
    tags=["Vector Infrastructure"],
)


@router.post(
    "/setup",
    response_model=VectorInfrastructureSetupResponse,
    status_code=status.HTTP_201_CREATED,
)
def setup_vector_infrastructure(
    request: VectorInfrastructureSetupRequest,
    service: VectorInfrastructureServiceDependency,
) -> VectorInfrastructureSetupResponse:
    """
    Configure vector infrastructure.

    For RAGOps-managed infrastructure, the configured provider may create
    the physical vector index if it does not already exist.

    For customer-managed infrastructure, the physical index must already
    exist and must be compatible with the requested configuration.
    """

    try:
        storage_provider = StorageProvider.LOCAL

        spec = VectorIndexSpec(
            index_name=request.index_name,
            namespace=request.namespace,
            dimensions=request.dimensions,
        )

        vector_index = service.setup(
            name=request.name,
            embedding_profile_id=request.embedding_profile_id,
            spec=spec,
            management_mode=request.management_mode,
            description=request.description,
            is_default=request.is_default,
            storage_provider=storage_provider,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return VectorInfrastructureSetupResponse.model_validate(
        vector_index,
    )


__all__ = [
    "router",
]