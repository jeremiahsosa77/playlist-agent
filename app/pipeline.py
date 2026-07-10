"""
Compatibility orchestration layer for Playlist Agent.

The public functions in this module are preserved for the command-line demo,
Braintrust evaluations, and future callers. Business responsibilities are
delegated to focused application services.
"""

from typing import Any

from app.services import (
    EvaluationService,
    PlaylistGenerationService,
    PublishingService,
    SpotifyService,
)


PlaylistData = dict[str, Any]
EvaluationScores = dict[str, float]
PublishedPlaylist = dict[str, Any]


playlist_generation_service = PlaylistGenerationService()
spotify_service = SpotifyService()
evaluation_service = EvaluationService()
publishing_service = PublishingService()


def generate_playlist(
    user_input: dict[str, Any],
) -> PlaylistData:
    """
    Generate a playlist using the configured LLM provider.
    """
    return playlist_generation_service.generate(
        user_input
    )


def enrich_playlist(
    playlist: PlaylistData,
) -> PlaylistData:
    """
    Add Spotify metadata to every generated song.
    """
    return spotify_service.enrich_playlist(
        playlist
    )


def evaluate_playlist(
    playlist: PlaylistData,
    expected_length: int,
) -> EvaluationScores:
    """
    Evaluate a playlist using deterministic scoring functions.
    """
    return evaluation_service.evaluate(
        playlist,
        expected_length,
    )


def passes_quality_gate(
    scores: EvaluationScores,
) -> bool:
    """
    Return whether the playlist meets publication requirements.
    """
    return evaluation_service.passes_quality_gate(
        scores
    )


def publish_playlist(
    playlist: PlaylistData,
    public: bool = True,
) -> PublishedPlaylist:
    """
    Publish an enriched playlist to the authenticated Spotify account.
    """
    return publishing_service.publish(
        playlist,
        public=public,
    )