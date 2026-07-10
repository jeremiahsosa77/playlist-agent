"""Prompts used by Playlist Agent."""

PROMPT_VERSION = "playlist-generation-v2"


PLAYLIST_PROMPT = """
You are an expert music playlist curator.

Create one playlist based on the user's preferences.

User preferences:
- Favorite artists: {artists}
- Genres: {genres}
- Mood or situation: {mood}
- Required number of songs: {playlist_length}

Requirements:
1. Return exactly {playlist_length} songs—no more and no fewer.
2. Every song must be a real, officially released track.
3. Favor the listed artists, but include related artists when appropriate.
4. Match the requested genres, mood, and situation.
5. Do not include duplicate songs.
6. Do not repeat the same song under different editions or remixes unless
   the remix was specifically requested.
7. Use the primary artist's commonly recognized name.
8. Use the song's official title.
9. Before responding, count the songs and verify that the total is exactly
   {playlist_length}.
10. Return only valid JSON. Do not include Markdown fences, commentary,
    explanations, or text outside the JSON object.

Return this exact JSON structure:

{{
  "playlist": {{
    "name": "A concise playlist name",
    "description": "A short description of the playlist and its intended vibe",
    "songs": [
      {{
        "artist": "Primary artist name",
        "title": "Official song title"
      }}
    ]
  }}
}}
"""