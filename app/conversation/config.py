"""Configuration for the adaptive playlist interview."""

import os


INTERVIEW_PROMPT_VERSION = os.getenv(
    "INTERVIEW_PROMPT_VERSION",
    "playlist-interview-v1",
).strip()

INTERVIEW_TEMPERATURE = float(
    os.getenv(
        "INTERVIEW_TEMPERATURE",
        "0.3",
    )
)

INTERVIEW_MAX_QUESTIONS = int(
    os.getenv(
        "INTERVIEW_MAX_QUESTIONS",
        "6",
    )
)

INTERVIEW_MAX_ATTEMPTS = int(
    os.getenv(
        "INTERVIEW_MAX_ATTEMPTS",
        "4",
    )
)

INTERVIEW_RETRY_BASE_SECONDS = float(
    os.getenv(
        "INTERVIEW_RETRY_BASE_SECONDS",
        "1.5",
    )
)

INTERVIEW_CONNECT_TIMEOUT_SECONDS = float(
    os.getenv(
        "INTERVIEW_CONNECT_TIMEOUT_SECONDS",
        "10",
    )
)

INTERVIEW_READ_TIMEOUT_SECONDS = float(
    os.getenv(
        "INTERVIEW_READ_TIMEOUT_SECONDS",
        "60",
    )
)

INTERVIEW_REQUEST_TIMEOUT = (
    INTERVIEW_CONNECT_TIMEOUT_SECONDS,
    INTERVIEW_READ_TIMEOUT_SECONDS,
)