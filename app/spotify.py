"""Spotify search and playlist-publishing helpers."""

import os

import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from app.config import SPOTIFY_REQUEST_TIMEOUT


load_dotenv()


SCOPE = (
    "playlist-modify-private "
    "playlist-modify-public"
)


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SCOPE,
    ),
    # Spotify searches may occasionally take longer than Spotipy's
    # default five-second timeout.
    requests_timeout=30,

    # Retry temporary network and Spotify server failures.
    retries=3,
    status_retries=3,
    backoff_factor=0.5,
)


def search_song(
    title: str,
    artist: str,
) -> dict | None:
    """
    Search Spotify for a song using progressively broader queries.
    """
    queries = [
        f'track:"{title}" artist:"{artist}"',
        f'"{title}" "{artist}"',
        f"{title} {artist}",
        title,
    ]

    for query in queries:
        try:
            results = sp.search(
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
        }

    return None


def create_playlist(
    name: str,
    description: str,
    track_uris: list[str],
    public: bool = False,
) -> dict:
    """
    Create a Spotify playlist and add the supplied track URIs.
    """
    if not track_uris:
        raise ValueError(
            "At least one Spotify track URI is required."
        )

    token = sp.auth_manager.get_access_token(
        as_dict=False
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    playlist_payload = {
        "name": name,
        "description": description,
        "public": public,
    }

    playlist_response = requests.post(
        "https://api.spotify.com/v1/me/playlists",
        headers=headers,
        json=playlist_payload,
        timeout=SPOTIFY_REQUEST_TIMEOUT,
    )

    playlist_response.raise_for_status()
    playlist = playlist_response.json()

    add_tracks_response = requests.post(
        (
            "https://api.spotify.com/v1/playlists/"
            f"{playlist['id']}/items"
        ),
        headers=headers,
        json={
            "uris": track_uris,
        },
        timeout=SPOTIFY_REQUEST_TIMEOUT,
    )

    add_tracks_response.raise_for_status()

    return {
        "id": playlist["id"],
        "name": playlist["name"],
        "url": playlist["external_urls"]["spotify"],
        "track_count": len(track_uris),
        "public": public,
    }