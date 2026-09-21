"""
Application service for vector infrastructure setup.

This service bridges the provider-neutral vector infrastructure provisioning
layer with the application's persistent VectorIndex model.

Responsibilities
----------------
- Decide whether infrastructure is RAGOps-managed or customer-managed.
- Delegate physical-index operations to the infrastructure provider.
- Persist the validated infrastructure configuration.
- Prevent duplicate VectorIndex records.
- Never delete customer-managed infrastructure.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.enums import (
    StorageProvider,
    VectorInfrastructureMode,
    VectorProvider,
)
from backend.models.vector_index import VectorIndex
from backend.vector_store.provisioning.base import (
    BaseVectorInfrastructureProvider,
)
from backend.vector_store.provisioning.models import VectorIndexSpec


class VectorInfrastructureSetupService:
    """
    Configure and persist a vector infrastructure definition.

    The service deliberately does not perform vector upserts, queries, or
    deletes. Physical infrastructure lifecycle operations are delegated to
    the provider-specific infrastructure provisioner.
    """

    def __init__(
        self,
        *,
        session: Session,
        infrastructure_provider: BaseVectorInfrastructureProvider,
    ) -> None:
        self._session = session
        self._infrastructure_provider = infrastructure_provider

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def setup(
        self,
        *,
        name: str,
        embedding_profile_id: UUID,
        spec: VectorIndexSpec,
        management_mode: VectorInfrastructureMode,
        description: str | None = None,
        is_default: bool = False,
        storage_provider: StorageProvider = StorageProvider.LOCAL,
    ) -> VectorIndex:
        """
        Configure vector infrastructure and persist its application record.

        RAGOPS_MANAGED
            Ensures the physical index exists and is compatible.

        CUSTOMER_MANAGED
            Validates that the physical index already exists and is compatible.
            No creation is attempted.

        Parameters
        ----------
        name:
            Human-readable application name for the vector index.

        embedding_profile_id:
            Persistent embedding profile associated with this vector index.

        spec:
            Desired physical vector-index characteristics.

        management_mode:
            Determines whether RAGOps may create the physical index.

        description:
            Optional human-readable description.

        is_default:
            Whether this should be the application's default vector index.

        storage_provider:
            Storage provider associated with the vector infrastructure record.

        Returns
        -------
        VectorIndex
            The newly created or existing persisted VectorIndex.

        Raises
        ------
        ValueError
            If customer-managed infrastructure does not exist, is
            incompatible, or an existing application record conflicts with
            the requested configuration.
        """

        provider = self._resolve_provider()

        existing = self._find_existing(
            provider=provider,
            index_name=spec.index_name,
        )

        if existing is not None:
            self._validate_existing_record(
                existing=existing,
                provider=provider,
                embedding_profile_id=embedding_profile_id,
                spec=spec,
                management_mode=management_mode,
            )

            return existing

        inspection = self._provision_or_validate(
            spec=spec,
            management_mode=management_mode,
        )

        if not inspection.exists:
            raise ValueError(
                f"Vector index {spec.index_name!r} does not exist "
                "after infrastructure setup."
            )

        vector_index = VectorIndex(
            embedding_profile_id=embedding_profile_id,
            name=name,
            description=description,
            provider=provider,
            index_name=spec.index_name,
            namespace=spec.namespace,
            dimensions=spec.dimensions,
            management_mode=management_mode,
            storage_provider=storage_provider,
            is_default=is_default,
            is_active=True,
        )

        self._session.add(vector_index)
        self._session.commit()
        self._session.refresh(vector_index)

        return vector_index

    # ------------------------------------------------------------------
    # Infrastructure operations
    # ------------------------------------------------------------------

    def _provision_or_validate(
        self,
        *,
        spec: VectorIndexSpec,
        management_mode: VectorInfrastructureMode,
    ):
        """
        Execute the appropriate provider operation for the ownership mode.
        """

        if management_mode == VectorInfrastructureMode.RAGOPS_MANAGED:
            return self._infrastructure_provider.ensure_index(
                spec=spec,
            )

        if management_mode == VectorInfrastructureMode.CUSTOMER_MANAGED:
            result = self._infrastructure_provider.validate_existing_index(
                spec=spec,
            )

            if not result.compatible:
                raise ValueError(result.summary)

            if result.inspection is None:
                raise ValueError(
                    f"Customer-managed vector index {spec.index_name!r} "
                    "was reported compatible but returned no inspection data."
                )

            return result.inspection

        raise ValueError(
            f"Unsupported vector infrastructure management mode: "
            f"{management_mode!r}"
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _find_existing(
        self,
        *,
        provider: VectorProvider,
        index_name: str,
    ) -> VectorIndex | None:
        """Find an existing application record for a physical index."""

        statement = select(VectorIndex).where(
            VectorIndex.provider == provider,
            VectorIndex.index_name == index_name,
            VectorIndex.deleted_at.is_(None),
        )

        return self._session.execute(statement).scalar_one_or_none()

    def _validate_existing_record(
        self,
        *,
        existing: VectorIndex,
        provider: VectorProvider,
        embedding_profile_id: UUID,
        spec: VectorIndexSpec,
        management_mode: VectorInfrastructureMode,
    ) -> None:
        """
        Ensure an existing application record agrees with the requested setup.
        """

        if existing.provider != provider:
            raise ValueError(
                "Existing VectorIndex provider does not match the requested "
                "infrastructure provider."
            )

        if existing.index_name != spec.index_name:
            raise ValueError(
                "Existing VectorIndex physical index name does not match "
                "the requested configuration."
            )

        if existing.namespace != spec.namespace:
            raise ValueError(
                "Existing VectorIndex namespace does not match the requested "
                "configuration."
            )

        if existing.dimensions != spec.dimensions:
            raise ValueError(
                "Existing VectorIndex dimensions do not match the requested "
                "configuration."
            )

        if existing.embedding_profile_id != embedding_profile_id:
            raise ValueError(
                "Existing VectorIndex embedding profile does not match "
                "the requested configuration."
            )

        if existing.management_mode != management_mode:
            raise ValueError(
                "Existing VectorIndex management mode does not match the "
                "requested configuration."
            )

        if not existing.is_active:
            raise ValueError(
                "Existing VectorIndex is inactive and cannot be reused."
            )

    # ------------------------------------------------------------------
    # Provider
    # ------------------------------------------------------------------

    def _resolve_provider(self) -> VectorProvider:
        """Resolve the shared application enum from the infrastructure provider."""

        provider_name = self._infrastructure_provider.provider_name

        try:
            return VectorProvider(provider_name.upper())
        except ValueError as exc:
            raise ValueError(
                f"Unsupported vector infrastructure provider: {provider_name!r}"
            ) from exc


__all__ = [
    "VectorInfrastructureSetupService",
]