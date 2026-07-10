"""FastAPI service dependencies."""

from app.services import (
    EvaluationService,
    PlaylistGenerationService,
    PublishingService,
    SpotifyService,
)


_playlist_generation_service = PlaylistGenerationService()
_spotify_service = SpotifyService()
_evaluation_service = EvaluationService()
_publishing_service = PublishingService()


def get_playlist_generation_service() -> PlaylistGenerationService:
    """
    Return the shared playlist-generation service.
    """
    return _playlist_generation_service


def get_spotify_service() -> SpotifyService:
    """
    Return the shared Spotify enrichment service.
    """
    return _spotify_service


def get_evaluation_service() -> EvaluationService:
    """
    Return the shared playlist evaluation service.
    """
    return _evaluation_service


def get_publishing_service() -> PublishingService:
    """
    Return the shared Spotify publishing service.
    """
    return _publishing_service