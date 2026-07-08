''' Evaluation entry point for the playlist agent. '''

import json
from dotenv import load_dotenv
from braintrust import Eval

from app.pipeline import generate_playlist, enrich_playlist, evaluate_playlist

load_dotenv()


def load_data():
    # Load evaluation examples from the local dataset file and map
    # each item into the shape expected by the Eval harness. The
    # `expected` field is reserved for ground-truth values when
    # available (not used in this dataset).
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
    # Compose the pipeline steps used by the evaluator: generate an
    # initial playlist and then enrich it with external metadata.
    playlist = generate_playlist(input)
    enriched_playlist = enrich_playlist(playlist)
    return enriched_playlist


def get_scores(input, output):
    # Run the shared evaluation routine that computes named quality
    # metrics for the supplied playlist output.
    return evaluate_playlist(
        output,
        expected_length=input["playlist_length"]
    )


def spotify_match_scorer(input, output, expected):
    # Extract the Spotify-match rate metric for the evaluator.
    return get_scores(input, output)["spotify_match"]


def duplicate_song_scorer(input, output, expected):
    # Return the duplicate-song check (1.0 == no duplicates).
    return get_scores(input, output)["duplicates"]


def playlist_length_scorer(input, output, expected):
    # Score whether the playlist length matches the requested length.
    return get_scores(input, output)["playlist_length"]


def spotify_match_confidence_scorer(input, output, expected):
    # Score how closely returned Spotify titles match the originals.
    return get_scores(input, output)["spotify_match_confidence"]


# Instantiate the Eval harness with the dataset, task function, and the
# list of scoring functions. `experiment_name` is used by the backend to
# group results.
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