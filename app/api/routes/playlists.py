"""Playlist generation API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_evaluation_service,
    get_playlist_generation_service,
    get_publishing_service,
    get_spotify_service,
)
from app.config import (
    LLM_PROVIDER,
    SPOTIFY_PUBLISHING_ENABLED,
    get_active_model,
)
from app.prompt import PROMPT_VERSION
from app.schemas import (
    GeneratePlaylistRequest,
    GeneratePlaylistResponse,
    PlaylistCandidate,
    PlaylistScores,
    PublishedPlaylist,
)
from app.services import (
    EvaluationService,
    PlaylistGenerationService,
    PublishingService,
    SpotifyService,
)


router = APIRouter(
    prefix="/playlists",
    tags=["Playlists"],
)


@router.post(
    "/generate",
    response_model=GeneratePlaylistResponse,
    response_model_by_alias=True,
)
def generate_playlist(
    request: GeneratePlaylistRequest,
    generation_service: Annotated[
        PlaylistGenerationService,
        Depends(get_playlist_generation_service),
    ],
    spotify_service: Annotated[
        SpotifyService,
        Depends(get_spotify_service),
    ],
    evaluation_service: Annotated[
        EvaluationService,
        Depends(get_evaluation_service),
    ],
    publishing_service: Annotated[
        PublishingService,
        Depends(get_publishing_service),
    ],
) -> GeneratePlaylistResponse:
    """
    Generate, enrich, evaluate, and optionally publish a playlist.
    """
    service_input = (
        request.to_service_input()
    )

    generated_playlist = (
        generation_service.generate(
            service_input
        )
    )

    enriched_playlist = (
        spotify_service.enrich_playlist(
            generated_playlist
        )
    )

    raw_scores = (
        evaluation_service.evaluate(
            enriched_playlist,
            expected_length=(
                request.playlist_length
            ),
        )
    )

    passed_quality_gate = (
        evaluation_service.passes_quality_gate(
            raw_scores
        )
    )

    scores = PlaylistScores(
        spotify_match=(
            raw_scores["spotify_match"]
        ),
        duplicate_score=(
            raw_scores["duplicates"]
        ),
        playlist_length=(
            raw_scores["playlist_length"]
        ),
        match_confidence=(
            raw_scores[
                "spotify_match_confidence"
            ]
        ),
    )

    publication: PublishedPlaylist | None = None
    published = False

    should_publish = (
        passed_quality_gate
        and SPOTIFY_PUBLISHING_ENABLED
    )

    if should_publish:
        publication_result = (
            publishing_service.publish(
                enriched_playlist,
                public=request.is_public,
            )
        )

        publication = (
            PublishedPlaylist.model_validate(
                publication_result
            )
        )
        published = True

    playlist = PlaylistCandidate.model_validate(
        enriched_playlist["playlist"]
    )

    return GeneratePlaylistResponse(
        playlist=playlist,
        scores=scores,
        passed_quality_gate=(
            passed_quality_gate
        ),
        published=published,
        publication=publication,
        provider=LLM_PROVIDER,
        model=get_active_model(),
        prompt_version=PROMPT_VERSION,
    )