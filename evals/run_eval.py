''' Evaluation entry point for the playlist agent. '''

import json
from dotenv import load_dotenv
from braintrust import Eval

from app.pipeline import generate_playlist, enrich_playlist, evaluate_playlist

load_dotenv()


def load_data():
    with open("evals/dataset.json", "r") as file:
        data = json.load(file)

    return [
        {
            "input": item,
            "expected": None,
        }
        for item in data
    ]


def task(input):
    playlist = generate_playlist(input)
    enriched_playlist = enrich_playlist(playlist)
    return enriched_playlist


def get_scores(input, output):
    return evaluate_playlist(
        output,
        expected_length=input["playlist_length"]
    )


def spotify_match_scorer(input, output, expected):
    return get_scores(input, output)["spotify_match"]


def duplicate_song_scorer(input, output, expected):
    return get_scores(input, output)["duplicates"]


def playlist_length_scorer(input, output, expected):
    return get_scores(input, output)["playlist_length"]


def spotify_match_confidence_scorer(input, output, expected):
    return get_scores(input, output)["spotify_match_confidence"]


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