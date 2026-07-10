"""Spotify enrichment application service."""

from collections.abc import Callable
from typing import Any

from app.spotify import search_song


PlaylistData = dict[str, Any]
SpotifySearchResult = dict[str, Any] | None
SpotifySearchFunction = Callable[
    [str, str],
    SpotifySearchResult,
]


class SpotifyService:
    """
    Enrich generated playlist songs with Spotify track metadata.

    Spotify search is injectable so enrichment behavior can be tested without
    performing real Spotify API calls.
    """

    def __init__(
        self,
        search_function: SpotifySearchFunction = search_song,
    ) -> None:
        self._search_function = search_function

    def enrich_playlist(
        self,
        playlist: PlaylistData,
    ) -> PlaylistData:
        """
        Add Spotify metadata to each song in a generated playlist.
        """
        songs = self._get_songs(playlist)

        for song in songs:
            title = song["title"]
            artist = song["artist"]

            spotify_match = self._search_function(
                title,
                artist,
            )

            song["spotify"] = spotify_match

            if spotify_match is None:
                print(
                    "NO MATCH: "
                    f"{artist} - {title}"
                )

        return playlist

    @staticmethod
    def _get_songs(
        playlist: PlaylistData,
    ) -> list[dict[str, Any]]:
        """
        Return the playlist songs after validating the expected structure.
        """
        if not isinstance(playlist, dict):
            raise TypeError(
                "Playlist enrichment requires a dictionary."
            )

        playlist_data = playlist.get("playlist")

        if not isinstance(playlist_data, dict):
            raise ValueError(
                "Playlist enrichment requires a 'playlist' object."
            )

        songs = playlist_data.get("songs")

        if not isinstance(songs, list):
            raise ValueError(
                "Playlist enrichment requires a songs list."
            )

        return songs