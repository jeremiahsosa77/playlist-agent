"""Spotify search and playlist-publishing helpers."""

import json
import os
from pathlib import Path
from threading import Lock

import requests
import spotipy
from dotenv import load_dotenv
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from app.config import SPOTIFY_REQUEST_TIMEOUT


load_dotenv()


SCOPE = (
    "playlist-modify-private "
    "playlist-modify-public"
)

CACHE_PATH = Path(".spotify_search_cache.json")
CACHE_LOCK = Lock()


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SCOPE,
    ),
    requests_timeout=30,
    status_forcelist=(500, 502, 503, 504),
    retries=3,
    status_retries=3,
    backoff_factor=0.5,
)


def normalize_cache_text(value: str) -> str:
    """Normalize song metadata for use in a cache key."""
    return " ".join(
        value.strip().lower().split()
    )


def build_cache_key(
    title: str,
    artist: str,
) -> str:
    """Build a stable cache key from a title and artist."""
    normalized_title = normalize_cache_text(title)
    normalized_artist = normalize_cache_text(artist)

    return f"{normalized_artist}::{normalized_title}"


def load_search_cache() -> dict:
    """Load the local Spotify search cache."""
    if not CACHE_PATH.exists():
        return {}

    try:
        with CACHE_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {}


def save_search_cache(cache: dict) -> None:
    """Safely write the Spotify search cache to disk."""
    temporary_path = CACHE_PATH.with_suffix(".tmp")

    with temporary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            cache,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_path.replace(CACHE_PATH)


SPOTIFY_SEARCH_CACHE = load_search_cache()


def search_song(
    title: str,
    artist: str,
) -> dict | None:
    """
    Search Spotify for a song using a local cache and progressively
    broader API queries.
    """
    cache_key = build_cache_key(
        title=title,
        artist=artist,
    )

    with CACHE_LOCK:
        cached_result = SPOTIFY_SEARCH_CACHE.get(
            cache_key
        )

    if cached_result is not None:
        print(
            f"Spotify cache hit: "
            f"{artist} - {title}"
        )
        return cached_result

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

        except SpotifyException as error:
            if error.http_status == 429:
                headers = error.headers or {}
                retry_after = headers.get(
                    "Retry-After",
                    "unknown",
                )

                raise RuntimeError(
                    "Spotify rate limit reached. "
                    f"Spotify requested a wait of "
                    f"{retry_after} seconds."
                ) from error

            print(
                "Spotify search failed for "
                f"{artist} - {title}: {error}"
            )
            continue

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

        spotify_result = {
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

        with CACHE_LOCK:
            SPOTIFY_SEARCH_CACHE[
                cache_key
            ] = spotify_result

            save_search_cache(
                SPOTIFY_SEARCH_CACHE
            )

        return spotify_result

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