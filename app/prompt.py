''' Store the prompt(s) '''

PLAYLIST_PROMPT = """
You are an expert music playlist curator.

Create a playlist based on this user input:

Favorite artists: {artists}
Genres: {genres}
Mood: {mood}
Playlist length: {playlist_length}

Return ONLY valid JSON in this format:

{{
  "playlist": {{
    "name": "...",
    "description": "...",
    "songs": [
      {{
        "artist": "...",
        "title": "..."
      }}
    ]
  }}
}}
"""