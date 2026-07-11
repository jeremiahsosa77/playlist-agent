"""Tests for provider and model configuration endpoints."""

from fastapi.testclient import TestClient


def test_providers_endpoint_returns_supported_providers(
    client: TestClient,
) -> None:
    """
    The API should identify all supported LLM providers.
    """
    response = client.get(
        "/api/providers"
    )

    assert response.status_code == 200

    data = response.json()

    assert "activeProvider" in data
    assert "providers" in data

    provider_ids = {
        provider["id"]
        for provider in data["providers"]
    }

    assert "gemini" in provider_ids
    assert "openrouter" in provider_ids

    for provider in data["providers"]:
        assert "name" in provider
        assert "enabled" in provider
        assert "active" in provider


def test_models_endpoint_returns_configured_models(
    client: TestClient,
) -> None:
    """
    The API should report models configured for supported providers.
    """
    response = client.get(
        "/api/models"
    )

    assert response.status_code == 200

    data = response.json()

    assert "activeModel" in data
    assert "models" in data
    assert len(data["models"]) >= 2

    model_providers = {
        model["provider"]
        for model in data["models"]
    }

    assert "gemini" in model_providers
    assert "openrouter" in model_providers

    for model in data["models"]:
        assert "id" in model
        assert "enabled" in model
        assert "active" in model