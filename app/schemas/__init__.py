"""Public request and response schemas for Playlist Agent."""

from app.schemas.common import APIModel
from app.schemas.configuration import (
    ModelInformation,
    ModelsResponse,
    ProviderInformation,
    ProvidersResponse,
)
from app.schemas.evaluation import (
    PlaylistScores,
    QualityGateResult,
)
from app.schemas.health import HealthResponse
from app.schemas.playlist import (
    GeneratePlaylistRequest,
    GeneratePlaylistResponse,
    GeneratedSong,
    PlaylistCandidate,
    PlaylistCandidateEnvelope,
    PublishedPlaylist,
    SpotifyTrack,
)

__all__ = [
    "APIModel",
    "GeneratePlaylistRequest",
    "GeneratePlaylistResponse",
    "GeneratedSong",
    "HealthResponse",
    "ModelInformation",
    "ModelsResponse",
    "PlaylistCandidate",
    "PlaylistCandidateEnvelope",
    "PlaylistScores",
    "ProviderInformation",
    "ProvidersResponse",
    "PublishedPlaylist",
    "QualityGateResult",
    "SpotifyTrack",
]