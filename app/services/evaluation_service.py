"""Playlist evaluation application service."""

from typing import Any

from app.config import (
    SPOTIFY_CONFIDENCE_THRESHOLD,
    SPOTIFY_MATCH_THRESHOLD,
)
from evals.scorers import (
    duplicate_song_score,
    playlist_length_score,
    spotify_match_confidence_score,
    spotify_match_rate,
)


PlaylistData = dict[str, Any]
EvaluationScores = dict[str, float]


class EvaluationService:
    """
    Evaluate playlist quality and apply publication thresholds.
    """

    def __init__(
        self,
        spotify_match_threshold: float = SPOTIFY_MATCH_THRESHOLD,
        spotify_confidence_threshold: float = (
            SPOTIFY_CONFIDENCE_THRESHOLD
        ),
    ) -> None:
        self._spotify_match_threshold = (
            spotify_match_threshold
        )
        self._spotify_confidence_threshold = (
            spotify_confidence_threshold
        )

    def evaluate(
        self,
        playlist: PlaylistData,
        expected_length: int,
    ) -> EvaluationScores:
        """
        Run the deterministic playlist scoring functions.
        """
        if (
            not isinstance(expected_length, int)
            or isinstance(expected_length, bool)
            or expected_length <= 0
        ):
            raise ValueError(
                "Expected playlist length must be a positive integer."
            )

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
            "spotify_match_confidence": (
                spotify_match_confidence_score(
                    playlist
                )
            ),
        }

    def passes_quality_gate(
        self,
        scores: EvaluationScores,
    ) -> bool:
        """
        Return whether all publication quality requirements are met.
        """
        self._validate_scores(scores)

        return (
            scores["spotify_match"]
            >= self._spotify_match_threshold
            and scores["spotify_match_confidence"]
            >= self._spotify_confidence_threshold
            and scores["duplicates"] == 1.0
            and scores["playlist_length"] == 1.0
        )

    @staticmethod
    def _validate_scores(
        scores: EvaluationScores,
    ) -> None:
        """
        Validate that all required quality scores are available.
        """
        required_scores = {
            "spotify_match",
            "duplicates",
            "playlist_length",
            "spotify_match_confidence",
        }

        missing_scores = sorted(
            required_scores.difference(scores)
        )

        if missing_scores:
            formatted_scores = ", ".join(missing_scores)

            raise ValueError(
                "Quality gate is missing required scores: "
                f"{formatted_scores}."
            )