"""Public request and response schemas for Playlist Agent."""

from app.schemas.common import APIModel
from app.schemas.evaluation import (
    PlaylistScores,
    QualityGateResult,
)
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
    "PlaylistCandidate",
    "PlaylistCandidateEnvelope",
    "PlaylistScores",
    "PublishedPlaylist",
    "QualityGateResult",
    "SpotifyTrack",
]