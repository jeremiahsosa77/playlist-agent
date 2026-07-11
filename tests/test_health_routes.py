"""Tests for API health endpoints."""

from fastapi.testclient import TestClient


def test_health_endpoint_returns_success(
    client: TestClient,
) -> None:
    """
    The health endpoint should report that the API is available.
    """
    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "Playlist Agent API"
    assert data["version"]
    assert data["environment"]