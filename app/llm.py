import json
import os
import requests
from dotenv import load_dotenv
from google import genai

from app.prompt import PLAYLIST_PROMPT

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def clean_json_response(text: str) -> dict:
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return json.loads(text)


def generate_playlist_with_llm(user_input: dict) -> dict:
    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "openrouter":
        return generate_with_openrouter(user_input)

    return generate_with_gemini(user_input)


def build_prompt(user_input: dict) -> str:
    return PLAYLIST_PROMPT.format(
        artists=", ".join(user_input["artists"]),
        genres=", ".join(user_input["genres"]),
        mood=user_input["mood"],
        playlist_length=user_input["playlist_length"],
    )


def generate_with_gemini(user_input: dict) -> dict:
    prompt = build_prompt(user_input)

    response = gemini_client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
    )

    return clean_json_response(response.text)


def generate_with_openrouter(user_input: dict) -> dict:
    prompt = build_prompt(user_input)

    model = os.getenv(
        "OPENROUTER_MODEL",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
    )

    print(f"Sending request to OpenRouter using {model}...")

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
                "X-OpenRouter-Title": "Playlist Agent",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": 0.7,
            },
            timeout=(10, 90),
        )

        print(f"OpenRouter status: {response.status_code}")

        if not response.ok:
            print(response.text)

        response.raise_for_status()

        data = response.json()
        text = data["choices"][0]["message"]["content"]

        print("Playlist received from OpenRouter.")

        return clean_json_response(text)

    except requests.Timeout as error:
        raise RuntimeError(
            "OpenRouter timed out. Try running it again or selecting a smaller free model."
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            f"OpenRouter request failed: {error}"
        ) from error