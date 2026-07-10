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
        "The Marias",
        "Daniel Caesar",
        "Steve Lacy",
        "Brent Faiyaz",
        "Kali Uchis",
        "Tame Impala",
        "Beabadoobee",
        "Faye Webster",
        "Mac DeMarco",
        "Men I Trust",
        "Laufey",
        "Malcolm Todd",
    ],
    "genres": [
        "Lo-Fi R&B",
        "Bedroom Pop",
        "Dream Pop",
        "Chill Indie Pop",
        "Alternative Soul",
        "Jazz Pop",
    ],
    "mood": (
        "Chill and upbeat vibes for a long drive, with a mix of "
        "relaxing and jam-worthy songs that keep the mood alive."
    ),
    "playlist_length": 10,
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