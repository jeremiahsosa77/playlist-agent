"""Braintrust evaluation entry point for Playlist Agent."""

import json
import threading

from braintrust import Eval
from dotenv import load_dotenv

from app.config import (
    GEMINI_MODEL,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    OPENROUTER_MODEL,
)
from app.pipeline import (
    enrich_playlist,
    evaluate_playlist,
    generate_playlist,
)
from app.prompt import PROMPT_VERSION


load_dotenv()


# Braintrust may run dataset cases concurrently. We currently serialize
# external API work to avoid overloading Spotify and free LLM providers.
TASK_LOCK = threading.Lock()


def load_data() -> list[dict]:
    """Load local evaluation cases in Braintrust's expected format."""
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
            "metadata": {
                "requested_length": item["playlist_length"],
                "mood": item["mood"],
                "genres": item["genres"],
            },
        }
        for item in data
    ]


def task(input: dict, hooks=None) -> dict:
    """Generate and enrich one playlist candidate."""
    if hooks is not None:
        hooks.metadata["provider"] = LLM_PROVIDER
        hooks.metadata["model"] = get_active_model()
        hooks.metadata["prompt_version"] = PROMPT_VERSION
        hooks.metadata["temperature"] = LLM_TEMPERATURE

    with TASK_LOCK:
        playlist = generate_playlist(input)
        return enrich_playlist(playlist)


def get_scores(
    input: dict,
    output: dict,
) -> dict:
    """Run the deterministic playlist evaluation."""
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


def get_active_model() -> str:
    """Return the model currently selected in configuration."""
    if LLM_PROVIDER == "openrouter":
        return OPENROUTER_MODEL

    if LLM_PROVIDER == "gemini":
        return GEMINI_MODEL

    return "unknown-model"


def sanitize_name(value: str) -> str:
    """Convert configuration text into a safe experiment-name segment."""
    return (
        value.strip()
        .lower()
        .replace("/", "-")
        .replace(":", "-")
        .replace(".", "-")
        .replace("_", "-")
    )


def get_experiment_name() -> str:
    """Build a descriptive name for this experiment configuration."""
    return "--".join(
        [
            sanitize_name(LLM_PROVIDER),
            sanitize_name(get_active_model()),
            sanitize_name(PROMPT_VERSION),
            f"temp-{str(LLM_TEMPERATURE).replace('.', '-')}",
        ]
    )


DATASET_SIZE = len(load_data())


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
    metadata={
        "provider": LLM_PROVIDER,
        "model": get_active_model(),
        "prompt_version": PROMPT_VERSION,
        "temperature": LLM_TEMPERATURE,
        "dataset_size": DATASET_SIZE,
        "pipeline_version": "v1.1",
    },
    tags=[
        LLM_PROVIDER,
        PROMPT_VERSION,
        "playlist-agent",
    ],
    description=(
        "Evaluates playlist generation, Spotify resolution, exact length, "
        "duplicate prevention, and title-match confidence."
    ),
)