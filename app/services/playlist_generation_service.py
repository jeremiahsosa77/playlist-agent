"""Playlist generation application service."""

from collections.abc import Callable
from typing import Any

from app.llm import generate_playlist_with_llm


PlaylistData = dict[str, Any]
PlaylistGenerator = Callable[[dict[str, Any]], PlaylistData]


class PlaylistGenerationService:
    """
    Generate playlist candidates through the configured LLM provider.

    The service depends on an injectable generation function so it can be
    tested without making real LLM requests.
    """

    def __init__(
        self,
        generator: PlaylistGenerator = generate_playlist_with_llm,
    ) -> None:
        self._generator = generator

    def generate(
        self,
        user_input: dict[str, Any],
    ) -> PlaylistData:
        """
        Generate and validate the basic structure of a playlist candidate.
        """
        self._validate_user_input(user_input)

        playlist = self._generator(user_input)

        self._validate_generated_playlist(playlist)

        return playlist

    @staticmethod
    def _validate_user_input(
        user_input: dict[str, Any],
    ) -> None:
        """
        Validate the minimum input required by the current generation prompt.
        """
        if not isinstance(user_input, dict):
            raise TypeError(
                "Playlist generation input must be a dictionary."
            )

        required_fields = {
            "artists",
            "genres",
            "mood",
            "playlist_length",
        }

        missing_fields = sorted(
            required_fields.difference(user_input)
        )

        if missing_fields:
            formatted_fields = ", ".join(missing_fields)

            raise ValueError(
                "Playlist generation input is missing required fields: "
                f"{formatted_fields}."
            )

        artists = user_input["artists"]
        genres = user_input["genres"]
        mood = user_input["mood"]
        playlist_length = user_input["playlist_length"]

        if not isinstance(artists, list):
            raise TypeError(
                "The 'artists' field must be a list."
            )

        if not isinstance(genres, list):
            raise TypeError(
                "The 'genres' field must be a list."
            )

        if not isinstance(mood, str) or not mood.strip():
            raise ValueError(
                "The 'mood' field must be a non-empty string."
            )

        if (
            not isinstance(playlist_length, int)
            or isinstance(playlist_length, bool)
            or playlist_length <= 0
        ):
            raise ValueError(
                "The 'playlist_length' field must be a positive integer."
            )

    @staticmethod
    def _validate_generated_playlist(
        playlist: PlaylistData,
    ) -> None:
        """
        Validate the minimum structure expected from an LLM response.
        """
        if not isinstance(playlist, dict):
            raise TypeError(
                "The generated playlist must be a dictionary."
            )

        playlist_data = playlist.get("playlist")

        if not isinstance(playlist_data, dict):
            raise ValueError(
                "The generated result must contain a 'playlist' object."
            )

        name = playlist_data.get("name")
        description = playlist_data.get("description")
        songs = playlist_data.get("songs")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "The generated playlist must have a non-empty name."
            )

        if (
            not isinstance(description, str)
            or not description.strip()
        ):
            raise ValueError(
                "The generated playlist must have a non-empty "
                "description."
            )

        if not isinstance(songs, list):
            raise ValueError(
                "The generated playlist must contain a songs list."
            )

        for index, song in enumerate(songs):
            if not isinstance(song, dict):
                raise ValueError(
                    f"Song at index {index} must be an object."
                )

            artist = song.get("artist")
            title = song.get("title")

            if not isinstance(artist, str) or not artist.strip():
                raise ValueError(
                    f"Song at index {index} must have a non-empty "
                    "artist."
                )

            if not isinstance(title, str) or not title.strip():
                raise ValueError(
                    f"Song at index {index} must have a non-empty "
                    "title."
                )