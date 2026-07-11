"""Unit tests for playlist application services."""

from typing import Any

import pytest

from app.services import (
    EvaluationService,
    PlaylistGenerationService,
    PublishingService,
    SpotifyService,
)


def build_playlist(
    song_count: int = 2,
) -> dict[str, Any]:
    """
    Build a small valid playlist for service tests.
    """
    return {
        "playlist": {
            "name": "Test Playlist",
            "description": "A playlist used for tests.",
            "songs": [
                {
                    "title": f"Song {index}",
                    "artist": f"Artist {index}",
                }
                for index in range(
                    1,
                    song_count + 1,
                )
            ],
        }
    }


def test_generation_service_uses_injected_generator() -> None:
    """
    The generation service should support a fake LLM function.
    """
    received_input: dict[str, Any] = {}

    def fake_generator(
        user_input: dict[str, Any],
    ) -> dict[str, Any]:
        received_input.update(user_input)

        return build_playlist(
            song_count=user_input[
                "playlist_length"
            ]
        )

    service = PlaylistGenerationService(
        generator=fake_generator
    )

    user_input = {
        "artists": [
            "The Marias",
        ],
        "genres": [
            "Dream Pop",
        ],
        "mood": "Late-night drive",
        "playlist_length": 2,
    }

    result = service.generate(
        user_input
    )

    assert received_input == user_input
    assert len(
        result["playlist"]["songs"]
    ) == 2


def test_generation_service_rejects_missing_fields() -> None:
    """
    Required generation fields must be present.
    """
    service = PlaylistGenerationService(
        generator=lambda user_input: build_playlist()
    )

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        service.generate(
            {
                "artists": [],
            }
        )


def test_spotify_service_enriches_every_song() -> None:
    """
    Spotify enrichment should attach metadata to each song.
    """
    search_calls: list[tuple[str, str]] = []

    def fake_search(
        title: str,
        artist: str,
    ) -> dict[str, Any]:
        search_calls.append(
            (
                title,
                artist,
            )
        )

        return {
            "id": f"{artist}-{title}",
            "uri": f"spotify:track:{artist}-{title}",
            "title": title,
            "artist": artist,
            "artists": [
                artist,
            ],
            "album": "Test Album",
            "spotify_url": (
                "https://open.spotify.com/track/test"
            ),
        }

    service = SpotifyService(
        search_function=fake_search
    )

    playlist = build_playlist()

    result = service.enrich_playlist(
        playlist
    )

    assert len(search_calls) == 2

    for song in result["playlist"]["songs"]:
        assert song["spotify"] is not None
        assert song["spotify"]["title"] == song["title"]


def test_evaluation_service_returns_expected_scores() -> None:
    """
    A complete, unique, fully matched playlist should score perfectly.
    """
    playlist = build_playlist()

    for song in playlist["playlist"]["songs"]:
        song["spotify"] = {
            "title": song["title"],
        }

    service = EvaluationService()

    scores = service.evaluate(
        playlist,
        expected_length=2,
    )

    assert scores == {
        "spotify_match": 1.0,
        "duplicates": 1.0,
        "playlist_length": 1.0,
        "spotify_match_confidence": 1.0,
    }


def test_evaluation_service_applies_thresholds() -> None:
    """
    Quality gates should use the configured service thresholds.
    """
    service = EvaluationService(
        spotify_match_threshold=0.90,
        spotify_confidence_threshold=0.80,
    )

    passing_scores = {
        "spotify_match": 0.95,
        "duplicates": 1.0,
        "playlist_length": 1.0,
        "spotify_match_confidence": 0.90,
    }

    failing_scores = {
        "spotify_match": 0.80,
        "duplicates": 1.0,
        "playlist_length": 1.0,
        "spotify_match_confidence": 0.90,
    }

    assert service.passes_quality_gate(
        passing_scores
    )
    assert not service.passes_quality_gate(
        failing_scores
    )


def test_publishing_service_passes_track_uris() -> None:
    """
    The publishing service should send only matched Spotify tracks.
    """
    publisher_arguments: dict[str, Any] = {}

    def fake_publisher(
        name: str,
        description: str,
        track_uris: list[str],
        public: bool,
    ) -> dict[str, Any]:
        publisher_arguments.update(
            {
                "name": name,
                "description": description,
                "track_uris": track_uris,
                "public": public,
            }
        )

        return {
            "id": "playlist-id",
            "name": name,
            "url": (
                "https://open.spotify.com/playlist/"
                "playlist-id"
            ),
            "track_count": len(track_uris),
            "public": public,
        }

    playlist = build_playlist()

    playlist["playlist"]["songs"][0]["spotify"] = {
        "uri": "spotify:track:first",
    }

    playlist["playlist"]["songs"][1]["spotify"] = None

    service = PublishingService(
        publisher=fake_publisher
    )

    result = service.publish(
        playlist,
        public=False,
    )

    assert publisher_arguments[
        "track_uris"
    ] == [
        "spotify:track:first",
    ]
    assert publisher_arguments["public"] is False
    assert result["track_count"] == 1


def test_publishing_service_rejects_no_matches() -> None:
    """
    A playlist with no Spotify matches must not be published.
    """
    playlist = build_playlist()

    for song in playlist["playlist"]["songs"]:
        song["spotify"] = None

    service = PublishingService(
        publisher=lambda *args: {}
    )

    with pytest.raises(
        ValueError,
        match="no valid Spotify tracks",
    ):
        service.publish(
            playlist
        )