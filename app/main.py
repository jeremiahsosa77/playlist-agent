'''
Entry point for the playlist-agent demo script.

This module demonstrates a simple, linear usage pattern of the
playlist pipeline: generate -> enrich -> evaluate -> (optional)
publish. It contains a few example `user_input` configurations that
can be swapped in for manual testing and quick local validation.

Note: This file is intended as a small runnable example and is not a
production entrypoint. For production use, consider wrapping the same
flow in a CLI or web service with proper error handling and retries.
'''

from app.pipeline import (
    generate_playlist,
    enrich_playlist,
    evaluate_playlist,
    passes_quality_gate,
    publish_playlist,
)

# Example input configurations. Uncomment or replace with realistic
# values to test different behaviors. Each configuration is a simple
# dictionary describing high-level playlist constraints used by the
# `generate_playlist` step. The fields are:
#  - artists: optional list of seed artists to bias the playlist
#  - genres: optional list of genres to include
#  - mood: free-form text describing the desired vibe
#  - playlist_length: desired number of tracks in the final playlist

'''
user_input = {
    "artists": ["Travis Scott", "Drake", "Metro Boomin"],
    "genres": ["Hip Hop", "Trap"],
    "mood": "Late Night Drive",
    "playlist_length": 20,
}
'''

'''
user_input = {
    "artists": ["Beabadoobee", "Laufey", "Clairo", "Faye Webster", "Mac DeMarco"],
    "genres": ["Hip Hop", "Trap", "Indie Rock", "Indie Pop", "Alternative", "Pop", "R&B"],
    "mood": "Chill Gaming Vibes",
    "playlist_length": 30,
}
'''

# Active test configuration used for this run. Update the values below
# to exercise different parts of the pipeline during development.
user_input = {
    "artists": ["Drake","Nickelback", "BigXthaPlug", "Destroy Lonely", "Tee Grizzley", "Future", "Gunna"],
    "genres": ["Hip Hop", "Trap", "Alternative", "Pop", "R&B", "Rock"],
    "mood": "Hype Gym Session but no old cringy songs",
    "playlist_length": 40,
}

# Step 1: Generate an initial playlist using the provided constraints.
playlist = generate_playlist(user_input)

# Step 2: Enrich the generated playlist with external metadata such as
# Spotify matches, durations, and canonical artist/track identifiers.
playlist = enrich_playlist(playlist)

# Step 3: Evaluate the playlist against a set of quality metrics. The
# `expected_length` parameter is used by the length-check scoring helper.
scores = evaluate_playlist(
    playlist,
    expected_length=user_input["playlist_length"]
)

# Output the evaluation scores to aid debugging and tuning.
print(scores)

# Step 4: Publish the playlist only when it passes the defined quality
# gate. The `passes_quality_gate` function centralizes the decision
# logic based on the evaluated scores.
if passes_quality_gate(scores):
    result = publish_playlist(playlist)
    print("Playlist created!")
    print(result)
else:
    print("Playlist did not pass quality gate.")