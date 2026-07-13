"""FastAPI service dependencies."""

from app.conversation import (
    ConfiguredInterviewProvider,
    ConversationService,
    InMemoryConversationSessionStore,
)
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

_conversation_session_store = (
    InMemoryConversationSessionStore()
)
_interview_decision_provider = (
    ConfiguredInterviewProvider()
)
_conversation_service = ConversationService(
    session_store=_conversation_session_store,
    decision_provider=_interview_decision_provider,
)


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


def get_conversation_service() -> ConversationService:
    """
    Return the shared adaptive interview service.
    """
    return _conversation_service