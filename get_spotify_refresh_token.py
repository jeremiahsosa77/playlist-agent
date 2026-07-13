"""Generate a Spotify refresh token for Playlist Agent."""

import os

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()


def get_required_value(name: str) -> str:
    value = os.getenv(name, "").strip()

    if not value:
        raise ValueError(
            f"{name} is missing from .env."
        )

    return value


def main() -> None:
    auth_manager = SpotifyOAuth(
        client_id=get_required_value(
            "SPOTIFY_CLIENT_ID"
        ),
        client_secret=get_required_value(
            "SPOTIFY_CLIENT_SECRET"
        ),
        redirect_uri=get_required_value(
            "SPOTIFY_REDIRECT_URI"
        ),
        scope=(
            "playlist-modify-public "
            "playlist-modify-private"
        ),
        cache_path=".spotify_user_cache",
        open_browser=True,
        show_dialog=True,
    )

    token_info = (
        auth_manager.get_access_token(
            as_dict=True
        )
    )

    refresh_token = token_info.get(
        "refresh_token"
    )

    if not refresh_token:
        raise RuntimeError(
            "Spotify did not return a refresh token."
        )

    print()
    print(
        "Refresh token created successfully."
    )
    print(
        "It has been saved in "
        ".spotify_user_cache."
    )


if __name__ == "__main__":
    main()