"""Playlist publishing application service."""

from collections.abc import Callable
from typing import Any

from app.spotify import create_playlist


PlaylistData = dict[str, Any]
PublishedPlaylist = dict[str, Any]
PlaylistPublisher = Callable[
    [str, str, list[str], bool],
    PublishedPlaylist,
]


class PublishingService:
    """
    Publish enriched playlists to Spotify.
    """

    def __init__(
        self,
        publisher: PlaylistPublisher = create_playlist,
    ) -> None:
        self._publisher = publisher

    def publish(
        self,
        playlist: PlaylistData,
        public: bool = True,
    ) -> PublishedPlaylist:
        """
        Publish all successfully matched Spotify tracks.
        """
        playlist_data = self._get_playlist_data(
            playlist
        )
        songs = playlist_data["songs"]

        track_uris = [
            song["spotify"]["uri"]
            for song in songs
            if song.get("spotify") is not None
        ]

        if not track_uris:
            raise ValueError(
                "The playlist contains no valid Spotify tracks."
            )

        return self._publisher(
            playlist_data["name"],
            playlist_data["description"],
            track_uris,
            public,
        )

    @staticmethod
    def _get_playlist_data(
        playlist: PlaylistData,
    ) -> dict[str, Any]:
        """
        Validate and return the generated playlist object.
        """
        if not isinstance(playlist, dict):
            raise TypeError(
                "Playlist publishing requires a dictionary."
            )

        playlist_data = playlist.get("playlist")

        if not isinstance(playlist_data, dict):
            raise ValueError(
                "Playlist publishing requires a 'playlist' object."
            )

        name = playlist_data.get("name")
        description = playlist_data.get("description")
        songs = playlist_data.get("songs")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "Playlist publishing requires a non-empty name."
            )

        if (
            not isinstance(description, str)
            or not description.strip()
        ):
            raise ValueError(
                "Playlist publishing requires a non-empty description."
            )

        if not isinstance(songs, list):
            raise ValueError(
                "Playlist publishing requires a songs list."
            )

        return playlist_data