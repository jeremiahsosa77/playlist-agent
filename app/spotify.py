"""Spotify integration helpers.

This module centralizes interactions with the Spotify Web API used by
the playlist pipeline: searching for tracks (`search_song`) and
creating playlists (`create_playlist`). Environment variables are
loaded from a `.env` file for local development.
"""

import os
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables (e.g. client id/secret, redirect URI).
load_dotenv()

# OAuth scopes required by the application when creating/modifying
# playlists on behalf of a user.
SCOPE = "playlist-modify-private playlist-modify-public"

# Initialize a Spotipy client that will handle token refresh and
# provide a convenient wrapper for common Spotify API calls used here.
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SCOPE,
    )
)

# Search Spotify for a track by title and artist and return the best match.
def search_song(title: str, artist: str):
    """Search Spotify for a track and return the best matching result.

    The function tries several query formats, from the most specific
    (explicit track/artist field search) to progressively looser
    queries to increase the chance of finding a match.

    Returns a small metadata dictionary for the first matching track,
    or `None` if no candidate is found.
    """

    # Try multiple query formats (specific -> general) to improve
    # matching across different Spotify metadata conventions.
    queries = [
        f'track:"{title}" artist:"{artist}"',
        f'"{title}" "{artist}"',
        f"{title} {artist}",
        title,
    ]

    for query in queries:
        # Use Spotipy's search helper; limiting to 1 returns the best
        # candidate and keeps the response small.
        results = sp.search(q=query, type="track", limit=1)
        tracks = results["tracks"]["items"]

        if tracks:
            track = tracks[0]

            # Return a compact dictionary with the fields the rest of
            # the pipeline expects.
            return {
                "id": track["id"],
                "uri": track["uri"],
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "spotify_url": track["external_urls"]["spotify"],
            }

    # No match found after trying all query strategies.
    return None

def create_playlist(name: str, description: str, track_uris: list[str], public: bool = False):
    """
    Create a Spotify playlist using the newer /me/playlists endpoint.
    """
    # Retrieve an access token from the Spotipy auth manager. This
    # method handles refreshing expired tokens when necessary.
    token = sp.auth_manager.get_access_token(as_dict=False)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Create the playlist on the user's account.
    playlist_payload = {
        "name": name,
        "description": description,
        "public": public,
    }

    playlist_response = requests.post(
        "https://api.spotify.com/v1/me/playlists",
        headers=headers,
        json=playlist_payload,
    )

    playlist_response.raise_for_status()
    playlist = playlist_response.json()

    # Add the requested tracks to the newly created playlist.
    add_tracks_response = requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist['id']}/items",
        headers=headers,
        json={"uris": track_uris},
    )

    add_tracks_response.raise_for_status()

    # Return a concise summary used by the caller for logging/UI.
    return {
        "id": playlist["id"],
        "name": playlist["name"],
        "url": playlist["external_urls"]["spotify"],
        "track_count": len(track_uris),
    }