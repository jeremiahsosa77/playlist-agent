"""Playlist evaluation request and response schemas."""

from app.schemas.common import APIModel


class PlaylistScores(APIModel):
    """
    Deterministic quality scores for a generated playlist.
    """

    spotify_match: float
    duplicate_score: float
    playlist_length: float
    match_confidence: float


class QualityGateResult(APIModel):
    """
    Result of applying publication thresholds to evaluation scores.
    """

    passed: bool
    scores: PlaylistScores