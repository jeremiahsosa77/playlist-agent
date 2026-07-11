"""Braintrust evaluation entry point for Playlist Agent."""

import threading
from typing import Any

from braintrust import Eval
from dotenv import load_dotenv

from app.pipeline import (
    enrich_playlist,
    evaluate_playlist,
    generate_playlist,
)
from evals.config import EvaluationConfig
from evals.dataset import load_dataset


load_dotenv()


# Braintrust may execute dataset cases concurrently. The current application
# uses shared external-service clients, so API work is serialized to improve
# reliability and reduce temporary rate-limit failures.
TASK_LOCK = threading.Lock()


def task(
    input: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate and enrich one playlist candidate.
    """
    with TASK_LOCK:
        playlist = generate_playlist(
            input
        )

        return enrich_playlist(
            playlist
        )


def get_scores(
    input: dict[str, Any],
    output: dict[str, Any],
) -> dict[str, float]:
    """
    Run the shared deterministic playlist evaluation.
    """
    return evaluate_playlist(
        output,
        expected_length=input[
            "playlist_length"
        ],
    )


def spotify_match_scorer(
    input: dict[str, Any],
    output: dict[str, Any],
    expected: Any,
) -> float:
    """
    Score the proportion of generated songs matched to Spotify.
    """
    return get_scores(
        input,
        output,
    )["spotify_match"]


def duplicate_song_scorer(
    input: dict[str, Any],
    output: dict[str, Any],
    expected: Any,
) -> float:
    """
    Score whether the playlist contains duplicate songs.
    """
    return get_scores(
        input,
        output,
    )["duplicates"]


def playlist_length_scorer(
    input: dict[str, Any],
    output: dict[str, Any],
    expected: Any,
) -> float:
    """
    Score whether the playlist contains the requested number of songs.
    """
    return get_scores(
        input,
        output,
    )["playlist_length"]


def spotify_match_confidence_scorer(
    input: dict[str, Any],
    output: dict[str, Any],
    expected: Any,
) -> float:
    """
    Score confidence in Spotify title matching.
    """
    return get_scores(
        input,
        output,
    )["spotify_match_confidence"]


dataset = load_dataset()

evaluation_config = EvaluationConfig.create(
    dataset_size=len(dataset),
)


Eval(
    evaluation_config.project_name,
    data=dataset,
    task=task,
    scores=[
        spotify_match_scorer,
        duplicate_song_scorer,
        playlist_length_scorer,
        spotify_match_confidence_scorer,
    ],
    experiment_name=(
        evaluation_config.experiment_name
    ),
    metadata=evaluation_config.metadata,
)