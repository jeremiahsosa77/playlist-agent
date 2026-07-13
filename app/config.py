"""Central application configuration."""

import os

from dotenv import load_dotenv


load_dotenv()


def get_boolean_environment_value(
    name: str,
    default: bool = False,
) -> bool:
    """
    Read a boolean environment variable safely.
    """
    default_value = "true" if default else "false"

    value = os.getenv(
        name,
        default_value,
    ).strip().lower()

    return value in {
        "1",
        "true",
        "yes",
        "on",
    }


APP_NAME = os.getenv(
    "APP_NAME",
    "Playlist Agent API",
).strip()

APP_VERSION = os.getenv(
    "APP_VERSION",
    "0.1.0",
).strip()

APP_ENVIRONMENT = os.getenv(
    "APP_ENVIRONMENT",
    "development",
).strip().lower()

API_PREFIX = os.getenv(
    "API_PREFIX",
    "/api",
).strip()

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "gemini",
).strip().lower()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
).strip()

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
).strip()

LLM_TEMPERATURE = float(
    os.getenv(
        "LLM_TEMPERATURE",
        "0.7",
    )
)

SPOTIFY_MATCH_THRESHOLD = float(
    os.getenv(
        "SPOTIFY_MATCH_THRESHOLD",
        "0.95",
    )
)

SPOTIFY_CONFIDENCE_THRESHOLD = float(
    os.getenv(
        "SPOTIFY_CONFIDENCE_THRESHOLD",
        "0.70",
    )
)

SPOTIFY_PUBLISHING_ENABLED = (
    get_boolean_environment_value(
        "SPOTIFY_PUBLISHING_ENABLED",
        default=True,
    )
)

SPOTIFY_REQUEST_TIMEOUT = (
    10,
    30,
)

OPENROUTER_REQUEST_TIMEOUT = (
    10,
    90,
)


def get_cors_origins() -> list[str]:
    """
    Return frontend origins allowed to call the API.
    """
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,"
        "http://127.0.0.1:3000",
    )

    return [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]


def get_active_model() -> str:
    """
    Return the model configured for the active provider.
    """
    if LLM_PROVIDER == "gemini":
        return GEMINI_MODEL

    if LLM_PROVIDER == "openrouter":
        return OPENROUTER_MODEL

    return os.getenv(
        "LLM_MODEL",
        "unknown-model",
    ).strip()