"""Shared pytest fixtures for Playlist Agent."""

import os
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_conversation_service,
    get_evaluation_service,
    get_playlist_generation_service,
    get_publishing_service,
    get_spotify_service,
)
from app.conversation import (
    PLAYLIST_BRIEF_VERSION,
    ConversationService,
    GeneratedTextInterviewProvider,
    InMemoryConversationSessionStore,
)
from app.main import app


TEST_INTERNAL_API_KEY = "playlist-agent-test-key"


class FakePlaylistGenerationService:
    """
    Return a predictable playlist without calling an LLM.
    """

    def generate(
        self,
        user_input: dict[str, Any],
    ) -> dict[str, Any]:
        playlist_length = user_input[
            "playlist_length"
        ]

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
                    "A predictable playlist used by "
                    "automated tests."
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
                "uri": (
                    f"spotify:track:track-{index}"
                ),
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
    Return predictable publication metadata.
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


def build_test_brief_json() -> str:
    """
    Return a valid playlist brief for fake model responses.
    """
    return f"""
    {{
      "version": "{PLAYLIST_BRIEF_VERSION}",
      "situation": "A high-energy late-night drive.",
      "mood": [
        "energetic",
        "confident"
      ],
      "energy": "high",
      "energy_curve": "Maintain strong energy throughout.",
      "preferred_artists": [],
      "preferred_genres": [
        "alternative R&B"
      ],
      "avoid_artists": [],
      "avoid_genres": [],
      "avoid_other": [],
      "familiarity": "mostly hidden gems",
      "explicit_content": null,
      "playlist_length": 20,
      "is_public": false,
      "additional_notes": null
    }}
    """.strip()


def build_fake_conversation_service() -> ConversationService:
    """
    Return an isolated interview service for API tests.
    """

    def fake_interview_generator(
        prompt: str,
    ) -> str:
        if "ready now" in prompt.lower():
            return f"""
            {{
              "action": "ready_to_generate",
              "question": null,
              "reasoning_summary": "The user supplied enough context.",
              "brief": {build_test_brief_json()}
            }}
            """

        return """
        {
          "action": "ask_question",
          "question": "Do you want familiar songs or hidden gems?",
          "reasoning_summary": "Discovery preference is missing.",
          "brief": null
        }
        """

    provider = GeneratedTextInterviewProvider(
        text_generator=(
            fake_interview_generator
        )
    )

    return ConversationService(
        session_store=(
            InMemoryConversationSessionStore()
        ),
        decision_provider=provider,
    )


@pytest.fixture
def fake_publishing_service() -> FakePublishingService:
    """
    Return a fresh fake publisher for each test.
    """
    return FakePublishingService()


@pytest.fixture
def conversation_service() -> ConversationService:
    """
    Return an isolated fake-backed interview service.
    """
    return build_fake_conversation_service()


@pytest.fixture
def client(
    fake_publishing_service: FakePublishingService,
    conversation_service: ConversationService,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """
    Create an authenticated client with external services replaced.
    """
    monkeypatch.setenv(
        "INTERNAL_API_KEY",
        TEST_INTERNAL_API_KEY,
    )

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

    app.dependency_overrides[
        get_conversation_service
    ] = lambda: conversation_service

    with TestClient(
        app,
        headers={
            "X-Playlist-Agent-Key": (
                TEST_INTERNAL_API_KEY
            ),
        },
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()