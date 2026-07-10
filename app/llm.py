"""LLM provider integrations for playlist generation."""

import json
import os
import time

import requests
from google import genai

from app.config import (
    GEMINI_MODEL,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    OPENROUTER_MODEL,
    OPENROUTER_REQUEST_TIMEOUT,
)
from app.prompt import PLAYLIST_PROMPT


gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def clean_json_response(text: str) -> dict:
    """
    Remove common Markdown code fences and parse an LLM response as JSON.
    """
    if not text:
        raise ValueError("The LLM returned an empty response.")

    cleaned_text = text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[len("```json"):].strip()
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[len("```"):].strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3].strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The LLM response was not valid JSON."
        ) from error


def build_prompt(user_input: dict) -> str:
    """
    Build the playlist-generation prompt from normalized user input.
    """
    return PLAYLIST_PROMPT.format(
        artists=", ".join(user_input["artists"]),
        genres=", ".join(user_input["genres"]),
        mood=user_input["mood"],
        playlist_length=user_input["playlist_length"],
    )


def generate_playlist_with_llm(user_input: dict) -> dict:
    """
    Generate a playlist with the active provider configured in `.env`.
    """
    if LLM_PROVIDER == "openrouter":
        return generate_with_openrouter(user_input)

    if LLM_PROVIDER == "gemini":
        return generate_with_gemini(user_input)

    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )


def generate_with_gemini(user_input: dict) -> dict:
    """
    Generate a playlist using Google Gemini.
    """
    prompt = build_prompt(user_input)

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return clean_json_response(response.text)


def get_retry_delay(
    response: requests.Response,
    attempt: int,
) -> int:
    """
    Read Retry-After for short temporary limits.

    Refuse very long waits, which normally indicate that the daily quota
    has been exhausted.
    """
    retry_after = response.headers.get("Retry-After")

    if retry_after:
        try:
            delay = max(int(float(retry_after)), 1)

            if delay > 300:
                raise RuntimeError(
                    "OpenRouter's daily free-model quota appears to be exhausted. "
                    f"The provider requested a wait of {delay} seconds. "
                    "Wait for the quota reset, select another available model, "
                    "or use paid credits."
                )

            return delay

        except ValueError:
            pass

    return min(2 ** attempt, 60)


def generate_with_openrouter(user_input: dict) -> dict:
    """
    Generate a playlist using an OpenRouter chat-completions model.

    Retries temporary rate limits and server errors using exponential
    backoff so one throttled request does not fail an entire eval run.
    """
    prompt = build_prompt(user_input)

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing from the environment."
        )

    max_attempts = 4

    for attempt in range(1, max_attempts + 1):
        print(
            f"Sending request to OpenRouter using "
            f"{OPENROUTER_MODEL} "
            f"(attempt {attempt}/{max_attempts})..."
        )

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "X-OpenRouter-Title": "Playlist Agent",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "temperature": LLM_TEMPERATURE,
                },
                timeout=OPENROUTER_REQUEST_TIMEOUT,
            )

        except requests.Timeout as error:
            if attempt == max_attempts:
                raise RuntimeError(
                    "OpenRouter timed out after multiple attempts."
                ) from error

            delay = min(2 ** attempt, 60)

            print(
                f"OpenRouter timed out. Retrying in "
                f"{delay} seconds..."
            )

            time.sleep(delay)
            continue

        except requests.RequestException as error:
            if attempt == max_attempts:
                raise RuntimeError(
                    f"OpenRouter request failed: {error}"
                ) from error

            delay = min(2 ** attempt, 60)

            print(
                f"OpenRouter request failed temporarily. "
                f"Retrying in {delay} seconds..."
            )

            time.sleep(delay)
            continue

        print(
            f"OpenRouter status: "
            f"{response.status_code}"
        )

        if response.status_code == 429:
            if attempt == max_attempts:
                raise RuntimeError(
                    "OpenRouter rate limit remained active after "
                    "multiple retry attempts."
                )

            delay = get_retry_delay(
                response,
                attempt,
            )

            print(
                f"OpenRouter rate limited the request. "
                f"Retrying in {delay} seconds..."
            )

            time.sleep(delay)
            continue

        if 500 <= response.status_code < 600:
            if attempt == max_attempts:
                raise RuntimeError(
                    "OpenRouter returned repeated server errors: "
                    f"{response.status_code} {response.text}"
                )

            delay = get_retry_delay(
                response,
                attempt,
            )

            print(
                f"OpenRouter provider error. "
                f"Retrying in {delay} seconds..."
            )

            time.sleep(delay)
            continue

        if not response.ok:
            raise RuntimeError(
                "OpenRouter returned an error: "
                f"{response.status_code} {response.text}"
            )

        data = response.json()
        choices = data.get("choices", [])

        if not choices:
            raise ValueError(
                "OpenRouter returned no completion choices."
            )

        text = choices[0]["message"]["content"]

        print("Playlist received from OpenRouter.")

        return clean_json_response(text)

    raise RuntimeError(
        "OpenRouter generation failed unexpectedly."
    )