"""Braintrust experiment metadata utilities."""

import subprocess
from typing import Any

from app.config import (
    APP_VERSION,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    get_active_model,
)
from app.prompt import PROMPT_VERSION


UNKNOWN_GIT_VALUE = "unavailable"


def run_git_command(
    *arguments: str,
) -> str:
    """
    Run a Git command and return its cleaned output.

    Evaluation runs should still work outside a Git repository, so Git
    failures return a safe fallback value instead of stopping the run.
    """
    try:
        result = subprocess.run(
            [
                "git",
                *arguments,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return UNKNOWN_GIT_VALUE

    output = result.stdout.strip()

    return output or UNKNOWN_GIT_VALUE


def get_git_branch() -> str:
    """
    Return the currently checked-out Git branch.
    """
    return run_git_command(
        "branch",
        "--show-current",
    )


def get_git_commit() -> str:
    """
    Return the abbreviated SHA for the current Git commit.
    """
    return run_git_command(
        "rev-parse",
        "--short",
        "HEAD",
    )


def get_git_commit_full() -> str:
    """
    Return the full SHA for the current Git commit.
    """
    return run_git_command(
        "rev-parse",
        "HEAD",
    )


def has_uncommitted_changes() -> bool | None:
    """
    Return whether the repository contains uncommitted changes.

    None is returned when Git information is unavailable.
    """
    status = run_git_command(
        "status",
        "--porcelain",
    )

    if status == UNKNOWN_GIT_VALUE:
        return None

    return bool(status)


def build_experiment_metadata(
    dataset_size: int,
) -> dict[str, Any]:
    """
    Build the shared metadata attached to a Braintrust experiment.
    """
    if dataset_size < 0:
        raise ValueError(
            "Dataset size cannot be negative."
        )

    return {
        "provider": LLM_PROVIDER,
        "model": get_active_model(),
        "prompt_version": PROMPT_VERSION,
        "temperature": LLM_TEMPERATURE,
        "dataset_size": dataset_size,
        "app_version": APP_VERSION,
        "git_branch": get_git_branch(),
        "git_commit": get_git_commit(),
        "git_commit_full": get_git_commit_full(),
        "git_dirty": has_uncommitted_changes(),
        "evaluation_type": "playlist_generation",
    }