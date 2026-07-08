''' Entry point of app '''

from app.pipeline import (
    generate_playlist,
    enrich_playlist,
    evaluate_playlist,
    passes_quality_gate,
    publish_playlist,
)
'''
user_input = {
    "artists": ["Travis Scott", "Drake", "Metro Boomin"],
    "genres": ["Hip Hop", "Trap"],
    "mood": "Late Night Drive",
    "playlist_length": 20,
}'''

user_input = {
    "artists": ["Beabadoobee", "Laufey", "Clairo", "Faye Webster", "Mac DeMarco"],
    "genres": ["Hip Hop", "Trap", "Indie Rock", "Indie Pop", "Alternative", "Pop", "R&B"],
    "mood": "Chill Gaming Vibes",
    "playlist_length": 30,
}

playlist = generate_playlist(user_input)
playlist = enrich_playlist(playlist)
scores = evaluate_playlist(
    playlist,
    expected_length=user_input["playlist_length"]
)

print(scores)

if passes_quality_gate(scores):
    result = publish_playlist(playlist)
    print("Playlist created!")
    print(result)
else:
    print("Playlist did not pass quality gate.")