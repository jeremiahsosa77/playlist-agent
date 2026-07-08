''' All spotify music interactions. '''

import os
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

SCOPE = "playlist-modify-private playlist-modify-public"

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

    """
    Search Spotify for a track by title and artist and return the best match.

    Returns a small metadata dictionary for the first matching track, or None
    when no track is found.
    """

    queries = [
        f'track:"{title}" artist:"{artist}"',
        f'"{title}" "{artist}"',
        f"{title} {artist}",
        title,
    ]

    for query in queries:
        results = sp.search(q=query, type="track", limit=1)
        tracks = results["tracks"]["items"]

        if tracks:
            track = tracks[0]

            return {
                "id": track["id"],
                "uri": track["uri"],
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "spotify_url": track["external_urls"]["spotify"],
            }

    return None

def create_playlist(name: str, description: str, track_uris: list[str], public: bool = False):
    """
    Create a Spotify playlist using the newer /me/playlists endpoint.
    """
    token = sp.auth_manager.get_access_token(as_dict=False)

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
    )

    playlist_response.raise_for_status()
    playlist = playlist_response.json()

    add_tracks_response = requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist['id']}/items",
        headers=headers,
        json={"uris": track_uris},
    )

    add_tracks_response.raise_for_status()

    return {
        "id": playlist["id"],
        "name": playlist["name"],
        "url": playlist["external_urls"]["spotify"],
        "track_count": len(track_uris),
    }