"""Playlist generation request and response schemas."""

from typing import Any

from pydantic import Field, field_validator

from app.schemas.common import APIModel
from app.schemas.evaluation import PlaylistScores


class GeneratePlaylistRequest(APIModel):
    """
    User preferences submitted to playlist generation.

    This contract intentionally matches the existing frontend request shape.
    """

    prompt: str = Field(
        min_length=1,
        max_length=2000,
    )
    artists: list[str] = Field(
        default_factory=list,
        max_length=50,
    )
    genres: list[str] = Field(
        default_factory=list,
        max_length=25,
    )
    playlist_length: int = Field(
        default=20,
        ge=1,
        le=100,
    )
    is_public: bool = True

    @field_validator(
        "artists",
        "genres",
    )
    @classmethod
    def validate_string_lists(
        cls,
        values: list[str],
    ) -> list[str]:
        """
        Remove blank values and duplicate entries while preserving order.
        """
        normalized_values: list[str] = []
        seen_values: set[str] = set()

        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    "Artists and genres must contain only strings."
                )

            normalized_value = value.strip()

            if not normalized_value:
                continue

            comparison_value = normalized_value.casefold()

            if comparison_value in seen_values:
                continue

            seen_values.add(comparison_value)
            normalized_values.append(normalized_value)

        return normalized_values

    def to_service_input(self) -> dict[str, Any]:
        """
        Convert the API request into the shape used by the generation service.

        The existing backend calls the user's description `mood`, while the
        frontend currently calls it `prompt`.
        """
        return {
            "artists": self.artists,
            "genres": self.genres,
            "mood": self.prompt,
            "playlist_length": self.playlist_length,
        }


class SpotifyTrack(APIModel):
    """
    Spotify metadata attached to a generated song.
    """

    id: str
    uri: str
    title: str
    artist: str
    artists: list[str]
    album: str
    spotify_url: str

    duration: str | None = None
    image_url: str | None = None


class GeneratedSong(APIModel):
    """
    One song returned in a generated playlist.
    """

    title: str
    artist: str
    spotify: SpotifyTrack | None = None


class PlaylistCandidate(APIModel):
    """
    Playlist content produced by the LLM and enriched through Spotify.
    """

    name: str
    description: str
    songs: list[GeneratedSong]


class PlaylistCandidateEnvelope(APIModel):
    """
    Envelope matching the current LLM playlist response structure.
    """

    playlist: PlaylistCandidate


class PublishedPlaylist(APIModel):
    """
    Spotify playlist metadata returned after publishing.
    """

    id: str
    name: str
    url: str
    track_count: int
    public: bool


class GeneratePlaylistResponse(APIModel):
    """
    Complete result returned by the future generation endpoint.
    """

    playlist: PlaylistCandidate
    scores: PlaylistScores
    passed_quality_gate: bool
    published: bool
    publication: PublishedPlaylist | None = None

    provider: str
    model: str
    prompt_version: str