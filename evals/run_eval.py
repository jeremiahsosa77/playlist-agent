"""Evaluation entry point for the playlist agent."""

import json
import os

from braintrust import Eval
from dotenv import load_dotenv

from app.pipeline import (
    enrich_playlist,
    evaluate_playlist,
    generate_playlist,
)

load_dotenv()


def load_data():
    """Load local evaluation cases in Braintrust's expected format."""
    with open("evals/dataset.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return [
        {
            "input": item,
            "expected": None,
        }
        for item in data
    ]


def task(input):
    """Generate and enrich one candidate playlist."""
    playlist = generate_playlist(input)
    return enrich_playlist(playlist)


def get_scores(input, output):
    """Run all shared deterministic playlist scorers."""
    return evaluate_playlist(
        output,
        expected_length=input["playlist_length"],
    )


def spotify_match_scorer(input, output, expected):
    return get_scores(input, output)["spotify_match"]


def duplicate_song_scorer(input, output, expected):
    return get_scores(input, output)["duplicates"]


def playlist_length_scorer(input, output, expected):
    return get_scores(input, output)["playlist_length"]


def spotify_match_confidence_scorer(input, output, expected):
    return get_scores(input, output)["spotify_match_confidence"]


def get_experiment_name() -> str:
    """
    Build an experiment name from the active provider and model.

    Examples:
    openrouter--nvidia-nemotron-3-ultra-550b-a55b-free
    gemini--gemini-2-5-flash
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "openrouter":
        model = os.getenv("OPENROUTER_MODEL", "unknown-model")
    else:
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    safe_model_name = (
        model.lower()
        .replace("/", "-")
        .replace(":", "-")
        .replace(".", "-")
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