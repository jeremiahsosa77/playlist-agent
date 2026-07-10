"""Braintrust evaluation entry point for Playlist Agent."""

import json
import os
import threading

from braintrust import Eval
from dotenv import load_dotenv

from app.pipeline import (
    enrich_playlist,
    evaluate_playlist,
    generate_playlist,
)


load_dotenv()


# Braintrust may execute dataset cases concurrently. The current MVP uses
# one shared Spotify client, so we serialize external API work to avoid
# overwhelming Spotify or hitting short network timeouts.
TASK_LOCK = threading.Lock()


def load_data() -> list[dict]:
    """
    Load local evaluation inputs in Braintrust's expected format.
    """
    with open(
        "evals/dataset.json",
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return [
        {
            "input": item,
            "expected": None,
        }
        for item in data
    ]


def task(input: dict) -> dict:
    """
    Generate and enrich one playlist candidate.

    External API work is currently serialized for reliability.
    """
    with TASK_LOCK:
        playlist = generate_playlist(input)
        return enrich_playlist(playlist)


def get_scores(
    input: dict,
    output: dict,
) -> dict:
    """
    Run the shared deterministic playlist evaluation.
    """
    return evaluate_playlist(
        output,
        expected_length=input["playlist_length"],
    )


def spotify_match_scorer(
    input,
    output,
    expected,
):
    return get_scores(
        input,
        output,
    )["spotify_match"]


def duplicate_song_scorer(
    input,
    output,
    expected,
):
    return get_scores(
        input,
        output,
    )["duplicates"]


def playlist_length_scorer(
    input,
    output,
    expected,
):
    return get_scores(
        input,
        output,
    )["playlist_length"]


def spotify_match_confidence_scorer(
    input,
    output,
    expected,
):
    return get_scores(
        input,
        output,
    )["spotify_match_confidence"]


def get_experiment_name() -> str:
    """
    Build a Braintrust experiment name from the active provider and model.
    """
    provider = os.getenv(
        "LLM_PROVIDER",
        "gemini",
    ).strip().lower()

    if provider == "openrouter":
        model = os.getenv(
            "OPENROUTER_MODEL",
            "unknown-model",
        )
    elif provider == "gemini":
        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )
    else:
        model = os.getenv(
            "LLM_MODEL",
            "unknown-model",
        )

    safe_model_name = (
        model.strip()
        .lower()
        .replace("/", "-")
        .replace(":", "-")
        .replace(".", "-")
        .replace("_", "-")
    )

    return f"{provider}--{safe_model_name}"


Eval(
    "Playlist Agent",
    data=load_data,
    task=task,
    scores=[
        spotify_match_scorer,
        duplicate_song_scorer,
        playlist_length_scorer,
        spotify_match_confidence_scorer,
    ],
    experiment_name=get_experiment_name(),
)