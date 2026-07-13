"""Spotify catalog search and playlist publishing helpers."""

import os
from typing import Any

import requests
import spotipy
from spotipy.oauth2 import (
    SpotifyClientCredentials,
)

from app.config import (
    SPOTIFY_REQUEST_TIMEOUT,
)


SPOTIFY_ACCOUNTS_TOKEN_URL = (
    "https://accounts.spotify.com/api/token"
)

SPOTIFY_API_BASE_URL = (
    "https://api.spotify.com/v1"
)


def get_required_environment_value(
    name: str,
) -> str:
    """
    Return a required environment variable or raise a clear error.
    """
    value = os.getenv(
        name,
        "",
    ).strip()

    if not value:
        raise ValueError(
            f"{name} is missing from the environment."
        )

    return value


def create_search_client() -> spotipy.Spotify:
    """
    Create a Spotify client for public catalog searches.

    Client Credentials authentication does not require a user login,
    browser redirect, or local token cache.
    """
    client_id = get_required_environment_value(
        "SPOTIFY_CLIENT_ID"
    )
    client_secret = get_required_environment_value(
        "SPOTIFY_CLIENT_SECRET"
    )

    authentication_manager = (
        SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
        )
    )

    return spotipy.Spotify(
        auth_manager=authentication_manager,
        requests_timeout=30,
        retries=3,
        status_retries=3,
        backoff_factor=0.5,
    )


_search_client: spotipy.Spotify | None = None


def get_search_client() -> spotipy.Spotify:
    """
    Return the shared lazily initialized Spotify search client.
    """
    global _search_client

    if _search_client is None:
        _search_client = create_search_client()

    return _search_client


def search_song(
    title: str,
    artist: str,
) -> dict[str, Any] | None:
    """
    Search Spotify for a song using progressively broader queries.
    """
    queries = [
        f'track:"{title}" artist:"{artist}"',
        f'"{title}" "{artist}"',
        f"{title} {artist}",
        title,
    ]

    client = get_search_client()

    for query in queries:
        try:
            results = client.search(
                q=query,
                type="track",
                limit=1,
            )
        except requests.RequestException as error:
            print(
                "Spotify search failed for "
                f"{artist} - {title}: {error}"
            )
            continue

        tracks = (
            results.get("tracks", {})
            .get("items", [])
        )

        if not tracks:
            continue

        track = tracks[0]

        album_images = (
            track.get("album", {})
            .get("images", [])
        )

        image_url = (
            album_images[0].get("url")
            if album_images
            else None
        )

        duration_ms = track.get(
            "duration_ms"
        )

        return {
            "id": track["id"],
            "uri": track["uri"],
            "title": track["name"],
            "artist": track["artists"][0]["name"],
            "artists": [
                item["name"]
                for item in track["artists"]
            ],
            "album": track["album"]["name"],
            "spotify_url": (
                track["external_urls"]["spotify"]
            ),
            "duration_ms": duration_ms,
            "image_url": image_url,
        }

    return None


def get_spotify_user_access_token() -> str:
    """
    Exchange the configured refresh token for a Spotify user access token.
    """
    client_id = get_required_environment_value(
        "SPOTIFY_CLIENT_ID"
    )
    client_secret = get_required_environment_value(
        "SPOTIFY_CLIENT_SECRET"
    )
    refresh_token = get_required_environment_value(
        "SPOTIFY_REFRESH_TOKEN"
    )

    response = requests.post(
        SPOTIFY_ACCOUNTS_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        auth=(
            client_id,
            client_secret,
        ),
        timeout=SPOTIFY_REQUEST_TIMEOUT,
    )

    if not response.ok:
        raise RuntimeError(
            "Spotify could not refresh the user "
            "access token: "
            f"{response.status_code} "
            f"{response.text}"
        )

    response_data = response.json()
    access_token = response_data.get(
        "access_token"
    )

    if not access_token:
        raise RuntimeError(
            "Spotify returned no user access token."
        )

    return access_token


def create_playlist(
    name: str,
    description: str,
    track_uris: list[str],
    public: bool = False,
) -> dict[str, Any]:
    """
    Create a Spotify playlist and add the supplied track URIs.
    """
    if not track_uris:
        raise ValueError(
            "At least one Spotify track URI is required."
        )

    access_token = (
        get_spotify_user_access_token()
    )

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Content-Type": "application/json",
    }

    playlist_response = requests.post(
        f"{SPOTIFY_API_BASE_URL}/me/playlists",
        headers=headers,
        json={
            "name": name,
            "description": description,
            "public": public,
        },
        timeout=SPOTIFY_REQUEST_TIMEOUT,
    )

    if not playlist_response.ok:
        raise RuntimeError(
            "Spotify playlist creation failed: "
            f"{playlist_response.status_code} "
            f"{playlist_response.text}"
        )

    playlist = playlist_response.json()

    add_tracks_response = requests.post(
        (
            f"{SPOTIFY_API_BASE_URL}/playlists/"
            f"{playlist['id']}/items"
        ),
        headers=headers,
        json={
            "uris": track_uris,
        },
        timeout=SPOTIFY_REQUEST_TIMEOUT,
    )

    if not add_tracks_response.ok:
        raise RuntimeError(
            "Spotify track insertion failed: "
            f"{add_tracks_response.status_code} "
            f"{add_tracks_response.text}"
        )

    return {
        "id": playlist["id"],
        "name": playlist["name"],
        "url": playlist[
            "external_urls"
        ]["spotify"],
        "track_count": len(track_uris),
        "public": public,
    }