''' Pipeline helpers for generating, enriching, and evaluating playlists. '''

import json
import os
from dotenv import load_dotenv
from google import genai

from app.prompt import PLAYLIST_PROMPT
from app.spotify import search_song
from evals.scorers import (
    spotify_match_rate,
    duplicate_song_score,
    playlist_length_score,
    spotify_match_confidence_score,
)

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Generates a playlist using the Gemini API.
def generate_playlist(user_input: dict) -> dict:
    prompt = PLAYLIST_PROMPT.format(
        artists=", ".join(user_input["artists"]),
        genres=", ".join(user_input["genres"]),
        mood=user_input["mood"],
        playlist_length=user_input["playlist_length"],
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)

# Enriches a playlist with Spotify metadata.
def enrich_playlist(playlist: dict) -> dict:
    # Add Spotify metadata to every song in the playlist.
    """
    Takes a playlist and adds Spotify data to each song.
    """
    # Loop through each song and look it up on Spotify.
    for song in playlist["playlist"]["songs"]:
        song["spotify"] = search_song(
            song["title"],
            song["artist"]
        )

        if song["spotify"] is None:
            print(f"NO MATCH: {song['artist']} - {song['title']}")
    # Return the updated playlist.
    return playlist

# Evaluates a playlist using various scoring functions.
def evaluate_playlist(playlist: dict) -> dict:
    # Compute the playlist quality metrics.
    return {
        # Measure how many songs matched Spotify.
        "spotify_match": spotify_match_rate(playlist),
        # Measure duplicate songs.
        "duplicates": duplicate_song_score(playlist),
        # Measure whether the playlist has the expected length.
        "playlist_length": playlist_length_score(playlist),
        # Measure the confidence of Spotify matches.
        "spotify_match_confidence": spotify_match_confidence_score(playlist),
    }