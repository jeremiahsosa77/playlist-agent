"""Pipeline helpers for generating, enriching, evaluating, and publishing playlists."""

from app.llm import generate_playlist_with_llm
from app.spotify import search_song, create_playlist
from evals.scorers import (
    spotify_match_rate,
    duplicate_song_score,
    playlist_length_score,
    spotify_match_confidence_score,
)


def generate_playlist(user_input: dict) -> dict:
    """
    Generate a playlist using the configured LLM provider.
    """
    return generate_playlist_with_llm(user_input)


def enrich_playlist(playlist: dict) -> dict:
    """
    Add Spotify metadata to every song in the playlist.
    """
    for song in playlist["playlist"]["songs"]:
        song["spotify"] = search_song(
            song["title"],
            song["artist"],
        )

        if song["spotify"] is None:
            print(f"NO MATCH: {song['artist']} - {song['title']}")

    return playlist


def evaluate_playlist(playlist: dict, expected_length: int) -> dict:
    """
    Evaluate the playlist using deterministic scoring functions.
    """
    return {
        "spotify_match": spotify_match_rate(playlist),
        "duplicates": duplicate_song_score(playlist),
        "playlist_length": playlist_length_score(
            playlist,
            expected_length,
        ),
        "spotify_match_confidence": spotify_match_confidence_score(
            playlist
        ),
    }


def passes_quality_gate(scores: dict) -> bool:
    """
    Decide whether the playlist is good enough to publish.
    """
    return (
        scores["spotify_match"] >= 0.95
        and scores["spotify_match_confidence"] >= 0.70
        and scores["duplicates"] == 1.0
        and scores["playlist_length"] == 1.0
    )


def publish_playlist(playlist: dict) -> dict:
    """
    Create the final playlist in Spotify.
    """
    songs = playlist["playlist"]["songs"]

    track_uris = [
        song["spotify"]["uri"]
        for song in songs
        if song.get("spotify") is not None
    ]

    return create_playlist(
        name=playlist["playlist"]["name"],
        description=playlist["playlist"]["description"],
        track_uris=track_uris,
        public=True,
    )