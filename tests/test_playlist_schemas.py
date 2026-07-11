"""Tests for playlist API request and response schemas."""

import pytest
from pydantic import ValidationError

from app.schemas import (
    GeneratePlaylistRequest,
    PlaylistCandidateEnvelope,
)


def test_generate_request_accepts_camel_case_fields() -> None:
    """
    Frontend-style camelCase input should validate correctly.
    """
    request = GeneratePlaylistRequest.model_validate(
        {
            "prompt": "Music for a late-night drive",
            "artists": [
                "The Marias",
                "Kali Uchis",
            ],
            "genres": [
                "Dream Pop",
            ],
            "playlistLength": 10,
            "isPublic": False,
        }
    )

    assert request.prompt == (
        "Music for a late-night drive"
    )
    assert request.playlist_length == 10
    assert request.is_public is False


def test_generate_request_converts_to_service_input() -> None:
    """
    The public API request should convert to the existing service format.
    """
    request = GeneratePlaylistRequest.model_validate(
        {
            "prompt": "Relaxed study music",
            "artists": [
                "Laufey",
            ],
            "genres": [
                "Jazz Pop",
            ],
            "playlistLength": 15,
            "isPublic": True,
        }
    )

    service_input = request.to_service_input()

    assert service_input == {
        "artists": [
            "Laufey",
        ],
        "genres": [
            "Jazz Pop",
        ],
        "mood": "Relaxed study music",
        "playlist_length": 15,
    }


def test_generate_request_removes_duplicate_preferences() -> None:
    """
    Duplicate artists and genres should be removed case-insensitively.
    """
    request = GeneratePlaylistRequest.model_validate(
        {
            "prompt": "A relaxed playlist",
            "artists": [
                "The Marias",
                "the marias",
                "Kali Uchis",
            ],
            "genres": [
                "Dream Pop",
                "dream pop",
            ],
            "playlistLength": 10,
            "isPublic": True,
        }
    )

    assert request.artists == [
        "The Marias",
        "Kali Uchis",
    ]

    assert request.genres == [
        "Dream Pop",
    ]


def test_generate_request_rejects_empty_prompt() -> None:
    """
    An empty playlist description should fail validation.
    """
    with pytest.raises(ValidationError):
        GeneratePlaylistRequest.model_validate(
            {
                "prompt": "",
                "artists": [],
                "genres": [],
                "playlistLength": 10,
                "isPublic": True,
            }
        )


def test_generate_request_rejects_invalid_length() -> None:
    """
    Playlist length must remain within the API limits.
    """
    with pytest.raises(ValidationError):
        GeneratePlaylistRequest.model_validate(
            {
                "prompt": "Workout music",
                "artists": [],
                "genres": [],
                "playlistLength": 0,
                "isPublic": True,
            }
        )

    with pytest.raises(ValidationError):
        GeneratePlaylistRequest.model_validate(
            {
                "prompt": "Workout music",
                "artists": [],
                "genres": [],
                "playlistLength": 101,
                "isPublic": True,
            }
        )


def test_playlist_candidate_envelope_validates() -> None:
    """
    A valid LLM playlist structure should pass schema validation.
    """
    result = PlaylistCandidateEnvelope.model_validate(
        {
            "playlist": {
                "name": "Midnight Motion",
                "description": (
                    "Dreamy songs for a late-night drive."
                ),
                "songs": [
                    {
                        "title": "Cariño",
                        "artist": "The Marias",
                    }
                ],
            }
        }
    )

    assert result.playlist.name == "Midnight Motion"
    assert len(result.playlist.songs) == 1
    assert (
        result.playlist.songs[0].artist
        == "The Marias"
    )