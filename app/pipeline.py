"""Core playlist generation, enrichment, evaluation, and publishing pipeline."""

from app.config import (
    SPOTIFY_CONFIDENCE_THRESHOLD,
    SPOTIFY_MATCH_THRESHOLD,
)
from app.llm import generate_playlist_with_llm
from app.spotify import create_playlist, search_song
from evals.scorers import (
    duplicate_song_score,
    playlist_length_score,
    spotify_match_confidence_score,
    spotify_match_rate,
)


def generate_playlist(user_input: dict) -> dict:
    """
    Generate a playlist using the configured LLM provider.
    """
    return generate_playlist_with_llm(user_input)


def enrich_playlist(playlist: dict) -> dict:
    """
    Add Spotify metadata to every generated song.
    """
    songs = playlist["playlist"]["songs"]

    for song in songs:
        song["spotify"] = search_song(
            title=song["title"],
            artist=song["artist"],
        )

        if song["spotify"] is None:
            print(
                f"NO MATCH: "
                f"{song['artist']} - {song['title']}"
            )

    return playlist


def evaluate_playlist(
    playlist: dict,
    expected_length: int,
) -> dict:
    """
    Evaluate a playlist using deterministic scoring functions.
    """
    return {
        "spotify_match": spotify_match_rate(
            playlist
        ),
        "duplicates": duplicate_song_score(
            playlist
        ),
        "playlist_length": playlist_length_score(
            playlist,
            expected_length,
        ),
        "spotify_match_confidence":
            spotify_match_confidence_score(
                playlist
            ),
    }


def passes_quality_gate(scores: dict) -> bool:
    """
    Return True when the playlist satisfies all publication thresholds.
    """
    return (
        scores["spotify_match"]
        >= SPOTIFY_MATCH_THRESHOLD
        and scores["spotify_match_confidence"]
        >= SPOTIFY_CONFIDENCE_THRESHOLD
        and scores["duplicates"] == 1.0
        and scores["playlist_length"] == 1.0
    )


def publish_playlist(
    playlist: dict,
    public: bool = True,
) -> dict:
    """
    Publish an enriched playlist to the authenticated Spotify account.
    """
    songs = playlist["playlist"]["songs"]

    track_uris = [
        song["spotify"]["uri"]
        for song in songs
        if song.get("spotify") is not None
    ]

    if not track_uris:
        raise ValueError(
            "The playlist contains no valid Spotify tracks."
        )

    return create_playlist(
        name=playlist["playlist"]["name"],
        description=playlist["playlist"]["description"],
        track_uris=track_uris,
        public=public,
    )