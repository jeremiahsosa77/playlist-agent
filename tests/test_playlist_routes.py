"""Tests for playlist generation API routes."""

from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_evaluation_service,
)
from app.main import app
from tests.conftest import (
    FailingEvaluationService,
    FakePublishingService,
)


def build_request() -> dict[str, Any]:
    """
    Return a valid frontend-style playlist request.
    """
    return {
        "prompt": (
            "Dreamy but upbeat music for a late-night drive"
        ),
        "artists": [
            "The Marias",
            "Kali Uchis",
        ],
        "genres": [
            "Dream Pop",
            "Alternative R&B",
        ],
        "playlistLength": 3,
        "isPublic": False,
    }


def test_generate_playlist_returns_complete_response(
    client: TestClient,
    fake_publishing_service: FakePublishingService,
) -> None:
    """
    A passing playlist should be enriched, scored, and published.
    """
    response = client.post(
        "/api/playlists/generate",
        json=build_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["playlist"]["name"] == (
        "Test Playlist"
    )
    assert len(
        data["playlist"]["songs"]
    ) == 3

    assert data["scores"] == {
        "spotifyMatch": 1.0,
        "duplicateScore": 1.0,
        "playlistLength": 1.0,
        "matchConfidence": 1.0,
    }

    assert data["passedQualityGate"] is True
    assert data["published"] is True

    assert data["publication"]["id"] == (
        "test-playlist-id"
    )
    assert data["publication"]["trackCount"] == 3
    assert data["publication"]["public"] is False

    assert data["provider"]
    assert data["model"]
    assert data["promptVersion"]

    assert (
        fake_publishing_service.publish_call_count
        == 1
    )


def test_generate_playlist_returns_spotify_metadata(
    client: TestClient,
) -> None:
    """
    Every generated song should contain enriched Spotify metadata.
    """
    response = client.post(
        "/api/playlists/generate",
        json=build_request(),
    )

    assert response.status_code == 200

    songs = response.json()[
        "playlist"
    ]["songs"]

    for song in songs:
        assert song["spotify"] is not None
        assert song["spotify"]["id"]
        assert song["spotify"]["uri"]
        assert song["spotify"]["spotifyUrl"]


def test_failed_quality_gate_does_not_publish(
    client: TestClient,
    fake_publishing_service: FakePublishingService,
) -> None:
    """
    Playlists that fail evaluation should be returned but not published.
    """
    app.dependency_overrides[
        get_evaluation_service
    ] = FailingEvaluationService

    response = client.post(
        "/api/playlists/generate",
        json=build_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["passedQualityGate"] is False
    assert data["published"] is False
    assert data["publication"] is None

    assert data["scores"]["spotifyMatch"] == 0.5
    assert data["scores"]["matchConfidence"] == 0.5

    assert (
        fake_publishing_service.publish_call_count
        == 0
    )


def test_generate_playlist_rejects_invalid_request(
    client: TestClient,
) -> None:
    """
    Invalid requests should return the structured API error shape.
    """
    response = client.post(
        "/api/playlists/generate",
        json={
            "prompt": "",
            "artists": [],
            "genres": [],
            "playlistLength": 0,
            "isPublic": True,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"]["code"] == (
        "REQUEST_VALIDATION_ERROR"
    )
    assert data["error"]["message"] == (
        "The request contained invalid data."
    )
    assert data["error"]["details"]


def test_generate_playlist_rejects_unknown_fields(
    client: TestClient,
) -> None:
    """
    Unknown request fields should not be silently accepted.
    """
    request_data = build_request()
    request_data["unknownField"] = "unexpected"

    response = client.post(
        "/api/playlists/generate",
        json=request_data,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == (
        "REQUEST_VALIDATION_ERROR"
    )

def test_generation_can_skip_spotify_publication(
    client: TestClient,
    fake_publishing_service: FakePublishingService,
    monkeypatch,
) -> None:
    """
    Generation should still succeed when production publishing is disabled.
    """
    import app.api.routes.playlists as playlists_route

    monkeypatch.setattr(
        playlists_route,
        "SPOTIFY_PUBLISHING_ENABLED",
        False,
    )

    response = client.post(
        "/api/playlists/generate",
        json=build_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["passedQualityGate"] is True
    assert data["published"] is False
    assert data["publication"] is None

    assert (
        fake_publishing_service.publish_call_count
        == 0
    )