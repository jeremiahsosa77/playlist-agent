''' Entry point of app '''

from app.pipeline import (
    generate_playlist,
    enrich_playlist,
    evaluate_playlist,
)

playlist = generate_playlist()
playlist = enrich_playlist(playlist)

scores = evaluate_playlist(playlist)

print(scores)