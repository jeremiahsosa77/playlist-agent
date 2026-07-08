''' Scoring helpers for playlist evaluation. '''

# Measures the rate of Spotify matches in the playlist.
def spotify_match_rate(playlist: dict) -> float:
    # Measure how many songs were matched to Spotify.
    songs = playlist["playlist"]["songs"]

    # Empty playlists score zero.
    if not songs:
        return 0.0

    # Count songs that have a Spotify result.
    matched = sum(1 for song in songs if song.get("spotify") is not None)

    # Return the matched fraction.
    return matched / len(songs)

# Checks for duplicate songs in the playlist.
def duplicate_song_score(playlist: dict) -> float:
    # Score 1.0 only when there are no duplicates.
    songs = playlist["playlist"]["songs"]

    # Track songs we have already seen.
    seen = set()

    # Compare normalized title/artist pairs.
    for song in songs:
        key = (
            song["title"].strip().lower(),
            song["artist"].strip().lower()
        )

        # Any repeated pair fails the score.
        if key in seen:
            return 0.0

        # Remember this song for later duplicate checks.
        seen.add(key)

    return 1.0

# Checks whether the playlist has the expected length.
def playlist_length_score(playlist: dict, expected_length: int) -> float:
    # Check whether the playlist has the expected number of songs.
    songs = playlist["playlist"]["songs"]

    # Exact length gets full credit.
    return 1.0 if len(songs) == expected_length else 0.0

# Checks how closely Spotify titles match the originals.
def spotify_match_confidence_score(playlist: dict) -> float:
    # Measure how closely Spotify titles match the originals.
    songs = playlist["playlist"]["songs"]

    # Empty playlists score zero.
    if not songs:
        return 0.0

    # Count the songs with a close title match.
    good_matches = 0

    # Compare each original song title with the returned Spotify title.
    for song in songs:
        spotify = song.get("spotify")

        # Skip songs that did not resolve on Spotify.
        if spotify is None:
            continue

        original_title = song["title"].lower()
        spotify_title = spotify["title"].lower()

        # Count close matches in either direction.
        if original_title in spotify_title or spotify_title in original_title:
            good_matches += 1

    # Return the fraction of songs with a confident match.
    return good_matches / len(songs)