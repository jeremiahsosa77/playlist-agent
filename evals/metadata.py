"""Braintrust experiment metadata utilities."""

import subprocess
from dataclasses import dataclass
from typing import Any

from app.config import (
    APP_VERSION,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    get_active_model,
)
from app.prompt import PROMPT_VERSION


UNKNOWN_GIT_VALUE = "unavailable"


@dataclass(frozen=True)
class GitCommandResult:
    """
    Result from attempting to run a Git command.
    """

    succeeded: bool
    output: str


def run_git_command(
    *arguments: str,
) -> GitCommandResult:
    """
    Run a Git command without interrupting evaluation on failure.

    Empty output is preserved because some successful Git commands,
    such as `git status --porcelain`, intentionally return nothing.
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
        return GitCommandResult(
            succeeded=False,
            output="",
        )

    return GitCommandResult(
        succeeded=True,
        output=result.stdout.strip(),
    )


def get_git_branch() -> str:
    """
    Return the currently checked-out Git branch.
    """
    result = run_git_command(
        "branch",
        "--show-current",
    )

    if not result.succeeded or not result.output:
        return UNKNOWN_GIT_VALUE

    return result.output


def get_git_commit() -> str:
    """
    Return the abbreviated SHA for the current Git commit.
    """
    result = run_git_command(
        "rev-parse",
        "--short",
        "HEAD",
    )

    if not result.succeeded or not result.output:
        return UNKNOWN_GIT_VALUE

    return result.output


def get_git_commit_full() -> str:
    """
    Return the full SHA for the current Git commit.
    """
    result = run_git_command(
        "rev-parse",
        "HEAD",
    )

    if not result.succeeded or not result.output:
        return UNKNOWN_GIT_VALUE

    return result.output


def has_uncommitted_changes() -> bool | None:
    """
    Return whether the repository contains uncommitted changes.

    False means Git succeeded and returned an empty status.
    None means Git status could not be determined.
    """
    result = run_git_command(
        "status",
        "--porcelain",
    )

    if not result.succeeded:
        return None

    return bool(result.output)


def build_experiment_metadata(
    dataset_size: int,
) -> dict[str, Any]:
    """
    Build metadata attached to a Braintrust experiment.
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