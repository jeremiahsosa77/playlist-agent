# Playlist Agent

Playlist Agent is an eval-driven AI playlist generator that turns natural-language music preferences into Spotify playlists.

The application uses a configurable LLM provider, currently Google Gemini or OpenRouter, to generate a structured playlist. Spotify then resolves each generated song to a real track, Braintrust evaluates the result, and only playlists that pass the configured quality gate are published.

## Features

- Generate playlists from artists, genres, mood, and requested length.
- Switch between Gemini and OpenRouter through environment variables.
- Enrich generated songs with Spotify metadata and track URIs.
- Score playlists for:
  - Spotify match rate
  - Duplicate songs
  - Requested playlist length
  - Spotify title-match confidence
- Publish passing playlists directly to Spotify.
- Run Braintrust experiments against multiple music-preference test cases.
- Automatically label Braintrust experiments with the active provider and model.

## Current Pipeline

```text
User preferences
→ Configured LLM generates a playlist
→ Spotify resolves generated songs
→ Playlist scorers evaluate the output
→ Quality gate checks the scores
→ Passing playlist is published to Spotify
```

## Tech Stack

Python 3.11+
Google Gemini API
OpenRouter
Spotify Web API
Spotipy
Braintrust
python-dotenv
Requests

## Project Structure

playlist-agent/
├── app/
│   ├── main.py          # Demo entry point
│   ├── pipeline.py      # Core playlist workflow
│   ├── llm.py           # Gemini and OpenRouter integrations
│   ├── prompt.py        # Playlist-generation prompt
│   ├── spotify.py       # Spotify search and publishing
│   └── config.py        # Central application configuration
│
├── evals/
│   ├── run_eval.py      # Braintrust evaluation entry point
│   ├── scorers.py       # Deterministic playlist scorers
│   ├── dataset.json     # Evaluation inputs
│   └── prompts.py       # Reserved for future prompt versions
│
├── tests/               # Reserved for automated tests
├── requirements.txt
├── .gitignore
└── README.md

## Setup

1. Create a virtual environment

  python -m venv .venv

2. Activate it (PowerShell):

  .\.venv\Scripts\Activate.ps1

3. Install dependencies

  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt

4. Create a .env file

Create a .env file in the project root:

# Active provider: gemini or openrouter
LLM_PROVIDER=openrouter

# Shared model settings
LLM_TEMPERATURE=0.7

# Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_openrouter_model

# Braintrust
BRAINTRUST_API_KEY=your_braintrust_api_key

# Spotify
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

## Switching Models

Use OpenRouter:

```bash
LLM_PROVIDER=openrouter
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
```

Use Gemini:

```bash
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
```

You can switch to another supported model by changing the relevant model ID in .env.

Braintrust experiment names are generated automatically from the active provider and model. Example:

```
openrouter--nvidia-nemotron-3-ultra-550b-a55b-free
```
## Running the Application

Update the user_input dictionary in app/main.py, then run:

```bash
python -m app.main
```

The application will:

- Generate a playlist using the configured LLM.
- Search Spotify for every generated song.
- Evaluate the playlist.
- Publish it when it passes the quality gate.
## Quality Gate

The current quality gate requires:

- Spotify match rate of at least 0.95
- Spotify title-match confidence of at least 0.70
- No duplicate songs
- Exact requested playlist length

These thresholds are stored in app/config.py.

## Running Braintrust Evaluations

Run:

```bash
python -m evals.run_eval
```

Evaluation inputs are stored in evals/dataset.json.

Each Braintrust run uses the same generate-and-enrich pipeline as the main application. The experiment name automatically includes the current provider and model so results can be compared across configurations.

Current Limitations
Spotify result confidence currently uses basic title matching.
The application does not yet use an LLM-as-a-judge scorer.
Braintrust does not yet capture token usage from direct Gemini or OpenRouter requests.
The demo publishes playlists publicly.
User feedback and long-term personalization are not implemented yet.
Planned Improvements
Add Pydantic request and response validation.
Add Braintrust tracing for model calls, latency, tokens, and errors.
Add LLM-as-a-judge scoring for mood and request adherence.
Compare models, prompts, and temperatures.
Add automatic retry and playlist refinement.
Store user likes, dislikes, skips, and playlist ratings.
Add a frontend and user onboarding flow.




https://openrouter.ai/
https://aistudio.google.com/
https://www.braintrust.dev/
https://developer.spotify.com/documentation/web-api
