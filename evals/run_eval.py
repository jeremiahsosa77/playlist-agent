''' Evaluation entry point for the playlist agent. '''

import json
from dotenv import load_dotenv
from braintrust import Eval

from app.pipeline import generate_playlist, enrich_playlist, evaluate_playlist

# Evaluation entry point for the playlist agent.
load_dotenv()


def load_data():
    # Load the evaluation dataset and wrap each item for Braintrust.
    with open("evals/dataset.json", "r") as file:
        data = json.load(file)

    # Convert raw dataset items into the expected input format.
    return [
        {
            "input": item,
            "expected": None,
        }
        for item in data
    ]

# Generate, then enrich, a playlist for scoring.
def task(input):
    playlist = generate_playlist(input)
    enriched_playlist = enrich_playlist(playlist)
    return enriched_playlist

# Score how many songs matched Spotify.
def spotify_match_scorer(input, output, expected):
    return evaluate_playlist(output)["spotify_match"]

# Score whether the playlist contains duplicates.
def duplicate_song_scorer(input, output, expected):
    return evaluate_playlist(output)["duplicates"]

# Score whether the playlist has the expected length.
def playlist_length_scorer(input, output, expected):
    return evaluate_playlist(output)["playlist_length"]

# Score how closely the Spotify results match the source songs.
def spotify_match_confidence_scorer(input, output, expected):
    return evaluate_playlist(output)["spotify_match_confidence"]


# Configure and run the Braintrust evaluation.
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
    experiment_name="gemini-spotify-v1",
)