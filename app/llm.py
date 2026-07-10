"""LLM provider integrations for playlist generation."""

import json
import os

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


def generate_with_openrouter(user_input: dict) -> dict:
    """
    Generate a playlist using an OpenRouter chat-completions model.
    """
    prompt = build_prompt(user_input)

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing from the environment."
        )

    print(
        f"Sending request to OpenRouter using "
        f"{OPENROUTER_MODEL}..."
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

        print(
            f"OpenRouter status: "
            f"{response.status_code}"
        )

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

    except requests.Timeout as error:
        raise RuntimeError(
            "OpenRouter timed out while generating the playlist."
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            f"OpenRouter request failed: {error}"
        ) from error