# Playlist Agent

Playlist Agent is an eval-driven AI playlist generator that turns natural language music preferences into Spotify playlists.

The pipeline uses Gemini to generate a structured playlist, resolves each generated track against the Spotify Web API, scores the result with local quality checks, and only publishes the playlist when it passes the configured quality gate.

## Features

- Generate playlist JSON from artists, genres, mood, and target length.
- Enrich generated tracks with Spotify metadata and canonical track URIs.
- Score playlists for Spotify match rate, duplicate tracks, requested length, and match confidence.
- Publish passing playlists to Spotify through user OAuth.
- Run Braintrust experiments against the local evaluation dataset.

## Tech Stack

- Python 3.11+
- Google Gemini API via `google-genai`
- Spotify Web API via `spotipy` and `requests`
- Braintrust for eval runs
- `python-dotenv` for local environment configuration

## Project Structure

```text
playlist-agent/
|-- app/
|   |-- main.py                 # Demo entry point for generate -> enrich -> evaluate -> publish
|   |-- pipeline.py             # Core playlist pipeline helpers
|   |-- prompt.py               # Gemini playlist-generation prompt
|   |-- spotify.py              # Spotify search and playlist publishing helpers
|   |-- config.py               # Reserved configuration module
|   |-- generated_playlist.json # Generated output artifact, when present
|   `-- enriched_playlist.json  # Enriched output artifact, when present
|-- evals/
|   |-- run_eval.py             # Braintrust evaluation entry point
|   |-- scorers.py              # Local scoring helpers
|   |-- dataset.json            # Evaluation examples
|   `-- prompts.py              # Reserved prompt-versioning module
|-- tests/                      # Reserved for automated tests
|-- requirements.txt
`-- README.md
```

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key
BRAINTRUST_API_KEY=your_braintrust_api_key

SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

The Spotify redirect URI must also be registered in your Spotify developer app settings.

## Usage

Update the `user_input` dictionary in `app/main.py`, then run the demo pipeline:

```powershell
python -m app.main
```

The demo performs the full flow:

1. Generate a playlist with Gemini.
2. Enrich songs with Spotify search results.
3. Evaluate the playlist quality.
4. Publish the playlist to Spotify if it passes the quality gate.

The current quality gate requires:

- Spotify match rate of at least `0.95`.
- Spotify match confidence of at least `0.70`.
- No duplicate songs.
- Exact requested playlist length.

## Running Evaluations

Run the Braintrust eval harness with:

```powershell
python -m evals.run_eval
```

Evaluation examples are stored in `evals/dataset.json`. The eval task runs the same generate-and-enrich pipeline used by the demo, then reports the scorers defined in `evals/scorers.py`.

## Notes

- `.env`, virtual environments, Python bytecode, and local cache files are ignored by Git.
- Spotify publishing requires an interactive OAuth flow the first time credentials are used.
- The current entry point is a development/demo script. A production CLI or service wrapper should add stronger input validation, retries, logging, and error handling.
