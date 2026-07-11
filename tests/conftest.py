"""Shared pytest fixtures for Playlist Agent."""

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_evaluation_service,
    get_playlist_generation_service,
    get_publishing_service,
    get_spotify_service,
)
from app.main import app


class FakePlaylistGenerationService:
    """
    Return a predictable playlist without calling an LLM.
    """

    def generate(
        self,
        user_input: dict[str, Any],
    ) -> dict[str, Any]:
        playlist_length = user_input["playlist_length"]

        songs = [
            {
                "title": f"Test Song {index}",
                "artist": f"Test Artist {index}",
            }
            for index in range(
                1,
                playlist_length + 1,
            )
        ]

        return {
            "playlist": {
                "name": "Test Playlist",
                "description": (
                    "A predictable playlist used by automated tests."
                ),
                "songs": songs,
            }
        }


class FakeSpotifyService:
    """
    Add predictable Spotify metadata without calling Spotify.
    """

    def enrich_playlist(
        self,
        playlist: dict[str, Any],
    ) -> dict[str, Any]:
        songs = playlist["playlist"]["songs"]

        for index, song in enumerate(
            songs,
            start=1,
        ):
            song["spotify"] = {
                "id": f"track-{index}",
                "uri": f"spotify:track:track-{index}",
                "title": song["title"],
                "artist": song["artist"],
                "artists": [
                    song["artist"],
                ],
                "album": "Test Album",
                "spotify_url": (
                    "https://open.spotify.com/track/"
                    f"track-{index}"
                ),
            }

        return playlist


class PassingEvaluationService:
    """
    Return perfect quality scores.
    """

    def evaluate(
        self,
        playlist: dict[str, Any],
        expected_length: int,
    ) -> dict[str, float]:
        return {
            "spotify_match": 1.0,
            "duplicates": 1.0,
            "playlist_length": 1.0,
            "spotify_match_confidence": 1.0,
        }

    def passes_quality_gate(
        self,
        scores: dict[str, float],
    ) -> bool:
        return True


class FailingEvaluationService:
    """
    Return scores that intentionally fail the quality gate.
    """

    def evaluate(
        self,
        playlist: dict[str, Any],
        expected_length: int,
    ) -> dict[str, float]:
        return {
            "spotify_match": 0.5,
            "duplicates": 1.0,
            "playlist_length": 1.0,
            "spotify_match_confidence": 0.5,
        }

    def passes_quality_gate(
        self,
        scores: dict[str, float],
    ) -> bool:
        return False


class FakePublishingService:
    """
    Return predictable publication metadata without calling Spotify.
    """

    def __init__(self) -> None:
        self.publish_call_count = 0

    def publish(
        self,
        playlist: dict[str, Any],
        public: bool = True,
    ) -> dict[str, Any]:
        self.publish_call_count += 1

        songs = playlist["playlist"]["songs"]

        return {
            "id": "test-playlist-id",
            "name": playlist["playlist"]["name"],
            "url": (
                "https://open.spotify.com/playlist/"
                "test-playlist-id"
            ),
            "track_count": len(songs),
            "public": public,
        }


@pytest.fixture
def fake_publishing_service() -> FakePublishingService:
    """
    Return a fresh fake publisher for each test.
    """
    return FakePublishingService()


@pytest.fixture
def client(
    fake_publishing_service: FakePublishingService,
) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI client with all external services replaced.
    """
    app.dependency_overrides[
        get_playlist_generation_service
    ] = FakePlaylistGenerationService

    app.dependency_overrides[
        get_spotify_service
    ] = FakeSpotifyService

    app.dependency_overrides[
        get_evaluation_service
    ] = PassingEvaluationService

    app.dependency_overrides[
        get_publishing_service
    ] = lambda: fake_publishing_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()