from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.models.enums import VectorInfrastructureMode


class VectorInfrastructureSetupRequest(BaseModel):
    """Request payload for configuring vector infrastructure."""

    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(..., min_length=1, max_length=255)
    embedding_profile_id: UUID
    provider: str = Field(..., min_length=1, max_length=100)
    index_name: str = Field(..., min_length=1, max_length=255)
    namespace: str = Field(..., min_length=1, max_length=255)
    dimensions: int = Field(..., gt=0)
    management_mode: VectorInfrastructureMode
    description: str | None = Field(default=None, max_length=1000)
    is_default: bool = False


class VectorInfrastructureSetupResponse(BaseModel):
    """Response returned after vector infrastructure setup."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID
    name: str
    provider: str
    index_name: str
    namespace: str
    dimensions: int
    management_mode: VectorInfrastructureMode
    embedding_profile_id: UUID
    storage_provider: str
    is_default: bool
    is_active: bool
    description: str | None = None