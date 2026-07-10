''' Store configuration. '''

"""Central application configuration."""

import os

from dotenv import load_dotenv

load_dotenv()


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

SPOTIFY_REQUEST_TIMEOUT = (
    10,
    30,
)

OPENROUTER_REQUEST_TIMEOUT = (
    10,
    90,
)