"""Runnable command-line demo for Playlist Agent."""

from app.pipeline import (
    enrich_playlist,
    evaluate_playlist,
    generate_playlist,
    passes_quality_gate,
    publish_playlist,
)


USER_INPUT = {
    "artists": [
        "Lil Tecca",
        "Kanye West",
        "21 Savage",
        "Brent Faiyaz",
        "NAV",
        "Chief Keef",
        "Travis Scott",
        "Drake",
        "Bryson Tiller",
        "Future",
        "Key Glock",
        "Gunna",
    ],
    "genres": [
        "R&B",
        "Chill Rap",
        "Dream Pop"
    ],
    "mood": (
        "Chill and smoke worthy vibes for a long drive, with a mix of "
        "newer and older jam worthy songs that keep the mood alive while everyone is vibing and singing along."
    ),
    "playlist_length": 75,
}


def main() -> None:
    """
    Run the complete playlist generation and publishing workflow.
    """
    print("Generating playlist...")

    playlist = generate_playlist(
        USER_INPUT
    )

    print("Enriching playlist with Spotify...")

    playlist = enrich_playlist(
        playlist
    )

    print("Evaluating playlist...")

    scores = evaluate_playlist(
        playlist,
        expected_length=USER_INPUT[
            "playlist_length"
        ],
    )

    print(scores)

    if not passes_quality_gate(scores):
        print(
            "Playlist did not pass the quality gate."
        )
        return

    print("Publishing playlist to Spotify...")

    result = publish_playlist(
        playlist,
        public=True,
    )

    print("Playlist created!")
    print(result)


if __name__ == "__main__":
    main()