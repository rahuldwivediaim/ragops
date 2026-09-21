from uuid import uuid4
from unittest.mock import Mock

from fastapi.testclient import TestClient

from backend.api.vector_infrastructure import router
from backend.common.dependency_injection.vector_infrastructure_dependencies import (
    get_vector_infrastructure_service,
)
from backend.main import app
from backend.models.enums import VectorInfrastructureMode


def _build_client(service: Mock) -> TestClient:
    app.include_router(router)
    app.dependency_overrides[get_vector_infrastructure_service] = lambda: service
    return TestClient(app)


def _build_vector_index() -> Mock:
    vector_index = Mock()
    vector_index.id = uuid4()
    vector_index.name = "HR Vector Index"
    vector_index.provider = "pinecone"
    vector_index.index_name = "ragops-hr"
    vector_index.namespace = "ragops-hr"
    vector_index.dimensions = 1536
    vector_index.management_mode = VectorInfrastructureMode.RAGOPS_MANAGED
    vector_index.embedding_profile_id = uuid4()
    vector_index.storage_provider = "local"
    vector_index.is_default = True
    vector_index.is_active = True
    vector_index.description = "HR knowledge base vector infrastructure"
    return vector_index


def test_setup_vector_infrastructure_returns_created_response():
    """The setup endpoint should return the persisted vector-index details."""

    service = Mock()
    vector_index = _build_vector_index()
    service.setup.return_value = vector_index

    client = _build_client(service)

    embedding_profile_id = vector_index.embedding_profile_id

    response = client.post(
        "/vector-infrastructure/setup",
        json={
            "name": "HR Vector Index",
            "embedding_profile_id": str(embedding_profile_id),
            "provider": "pinecone",
            "index_name": "ragops-hr",
            "namespace": "ragops-hr",
            "dimensions": 1536,
            "management_mode": "RAGOPS_MANAGED",
            "description": "HR knowledge base vector infrastructure",
            "is_default": True,
        },
    )

    print("\nAPI setup response:")
    print(response.status_code)
    print(response.json())

    assert response.status_code == 201

    body = response.json()

    assert body["id"] == str(vector_index.id)
    assert body["name"] == "HR Vector Index"
    assert body["provider"] == "pinecone"
    assert body["index_name"] == "ragops-hr"
    assert body["namespace"] == "ragops-hr"
    assert body["dimensions"] == 1536
    assert body["management_mode"] == "RAGOPS_MANAGED"
    assert body["embedding_profile_id"] == str(embedding_profile_id)
    assert body["is_default"] is True
    assert body["is_active"] is True

    service.setup.assert_called_once()


def test_setup_vector_infrastructure_passes_customer_managed_mode():
    """Customer-managed configuration should be delegated to the service."""

    service = Mock()
    vector_index = _build_vector_index()
    vector_index.management_mode = VectorInfrastructureMode.CUSTOMER_MANAGED
    vector_index.is_default = False
    service.setup.return_value = vector_index

    client = _build_client(service)

    response = client.post(
        "/vector-infrastructure/setup",
        json={
            "name": "Customer HR Index",
            "embedding_profile_id": str(vector_index.embedding_profile_id),
            "provider": "pinecone",
            "index_name": "customer-hr",
            "namespace": "ragops-hr",
            "dimensions": 1536,
            "management_mode": "CUSTOMER_MANAGED",
            "is_default": False,
        },
    )

    print("\nCustomer-managed API response:")
    print(response.status_code)
    print(response.json())

    assert response.status_code == 201

    service.setup.assert_called_once()

    call_kwargs = service.setup.call_args.kwargs

    assert (
        call_kwargs["management_mode"]
        == VectorInfrastructureMode.CUSTOMER_MANAGED
    )
    assert call_kwargs["embedding_profile_id"] == vector_index.embedding_profile_id
    assert call_kwargs["is_default"] is False


def test_setup_vector_infrastructure_maps_value_error_to_conflict():
    """Business validation errors should be returned as HTTP 409."""

    service = Mock()
    service.setup.side_effect = ValueError(
        "Vector index configuration is incompatible."
    )

    client = _build_client(service)

    response = client.post(
        "/vector-infrastructure/setup",
        json={
            "name": "HR Vector Index",
            "embedding_profile_id": str(uuid4()),
            "provider": "pinecone",
            "index_name": "ragops-hr",
            "namespace": "ragops-hr",
            "dimensions": 1536,
            "management_mode": "CUSTOMER_MANAGED",
        },
    )

    print("\nValidation error response:")
    print(response.status_code)
    print(response.json())

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Vector index configuration is incompatible."
    )


def test_setup_vector_infrastructure_maps_runtime_error_to_service_unavailable():
    """Infrastructure availability errors should be returned as HTTP 503."""

    service = Mock()
    service.setup.side_effect = RuntimeError(
        "PINECONE_API_KEY is not configured."
    )

    client = _build_client(service)

    response = client.post(
        "/vector-infrastructure/setup",
        json={
            "name": "HR Vector Index",
            "embedding_profile_id": str(uuid4()),
            "provider": "pinecone",
            "index_name": "ragops-hr",
            "namespace": "ragops-hr",
            "dimensions": 1536,
            "management_mode": "RAGOPS_MANAGED",
        },
    )

    print("\nInfrastructure error response:")
    print(response.status_code)
    print(response.json())

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "PINECONE_API_KEY is not configured."
    )


def test_setup_vector_infrastructure_rejects_invalid_request():
    """Invalid request data should be rejected by Pydantic/FastAPI."""

    service = Mock()
    client = _build_client(service)

    response = client.post(
        "/vector-infrastructure/setup",
        json={
            "name": "",
            "embedding_profile_id": "not-a-uuid",
            "provider": "pinecone",
            "index_name": "ragops-hr",
            "namespace": "ragops-hr",
            "dimensions": 0,
            "management_mode": "RAGOPS_MANAGED",
        },
    )

    print("\nInvalid request response:")
    print(response.status_code)
    print(response.json())

    assert response.status_code == 422
    service.setup.assert_not_called()