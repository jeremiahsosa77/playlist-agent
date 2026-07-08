# Playlist Agent

Playlist Agent is an eval-driven AI playlist generator that creates personalized Spotify playlists from natural language preferences.

The user provides favorite artists, genres, mood, or a situation. Gemini generates a structured playlist, Spotify validates and enriches the songs with real track data, and Braintrust evaluates the playlist before it is accepted.

## Current Features

- Generate playlist JSON with Gemini
- Search and enrich tracks using Spotify Web API
- Evaluate playlists with Braintrust
- Score Spotify match rate
- Detect duplicate songs
- Validate playlist length
- Score Spotify match confidence

## Tech Stack

- Python
- Gemini API
- Spotify Web API
- Spotipy
- Braintrust
- python-dotenv

## Project Structure

```text
playlist-agent/
├── app/
│   ├── main.py
│   ├── pipeline.py
│   ├── prompt.py
│   ├── spotify.py
│   └── config.py
│
├── evals/
│   ├── run_eval.py
│   ├── scorers.py
│   ├── dataset.json
│   └── prompts.py
│
├── .env
├── requirements.txt
└── README.md


SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

GEMINI_API_KEY=your_gemini_api_key
BRAINTRUST_API_KEY=your_braintrust_api_key

python -m evals.run_eval