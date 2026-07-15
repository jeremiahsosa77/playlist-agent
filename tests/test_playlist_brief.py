"""Tests for structured playlist interview briefs."""

import json

import pytest
from pydantic import ValidationError

from app.conversation import (
    PLAYLIST_BRIEF_VERSION,
    InterviewActionType,
    InterviewResponseParseError,
    PlaylistBrief,
    parse_interview_action,
)


def valid_brief_data() -> dict[str, object]:
    """
    Return one complete valid playlist brief payload.
    """
    return {
        "version": PLAYLIST_BRIEF_VERSION,
        "situation": (
            "A nighttime drive from San Antonio "
            "to Houston."
        ),
        "mood": [
            "cinematic",
            "confident",
        ],
        "energy": "medium-high",
        "energy_curve": (
            "Begin smoothly and build toward "
            "a high-energy finish."
        ),
        "preferred_artists": [
            "The Weeknd",
        ],
        "preferred_genres": [
            "alternative R&B",
            "hip-hop",
        ],
        "avoid_artists": [],
        "avoid_genres": [
            "country",
        ],
        "avoid_other": [
            "overly sad songs",
        ],
        "familiarity": "balanced",
        "explicit_content": True,
        "playlist_length": 20,
        "is_public": False,
        "additional_notes": (
            "Prioritize smooth transitions."
        ),
    }


def test_playlist_brief_accepts_valid_data() -> None:
    """
    A complete playlist brief should validate.
    """
    brief = PlaylistBrief.model_validate(
        valid_brief_data()
    )

    assert brief.version == PLAYLIST_BRIEF_VERSION
    assert brief.playlist_length == 20
    assert brief.is_public is False
    assert brief.mood == [
        "cinematic",
        "confident",
    ]


def test_playlist_brief_applies_safe_defaults() -> None:
    """
    Optional preferences should receive stable defaults.
    """
    brief = PlaylistBrief(
        situation="Music for an evening study session."
    )

    assert brief.version == PLAYLIST_BRIEF_VERSION
    assert brief.mood == []
    assert brief.preferred_artists == []
    assert brief.preferred_genres == []
    assert brief.avoid_artists == []
    assert brief.avoid_genres == []
    assert brief.avoid_other == []
    assert brief.playlist_length == 20
    assert brief.is_public is False
    assert brief.explicit_content is None


def test_playlist_brief_rejects_invalid_length() -> None:
    """
    Playlist length must stay inside supported limits.
    """
    with pytest.raises(ValidationError):
        PlaylistBrief(
            situation="A workout.",
            playlist_length=3,
        )


def test_parser_accepts_ready_action_with_brief() -> None:
    """
    A ready model response with a valid brief should parse.
    """
    response = json.dumps(
        {
            "action": "ready_to_generate",
            "question": None,
            "reasoning_summary": (
                "The occasion, mood, and music "
                "direction are clear."
            ),
            "brief": valid_brief_data(),
        }
    )

    action = parse_interview_action(
        response
    )

    assert (
        action.action
        == InterviewActionType.READY_TO_GENERATE
    )
    assert action.brief is not None
    assert action.brief.situation.startswith(
        "A nighttime drive"
    )


def test_parser_rejects_ready_action_without_brief() -> None:
    """
    LLM ready responses must include a playlist brief.
    """
    response = json.dumps(
        {
            "action": "ready_to_generate",
            "question": None,
            "reasoning_summary": (
                "The interview has enough context."
            ),
            "brief": None,
        }
    )

    with pytest.raises(
        InterviewResponseParseError,
        match="must include a playlist brief",
    ):
        parse_interview_action(
            response
        )


def test_parser_rejects_invalid_brief() -> None:
    """
    Invalid brief fields should reject the entire model response.
    """
    invalid_brief = valid_brief_data()
    invalid_brief["playlist_length"] = 500

    response = json.dumps(
        {
            "action": "ready_to_generate",
            "question": None,
            "reasoning_summary": (
                "The interview has enough context."
            ),
            "brief": invalid_brief,
        }
    )

    with pytest.raises(
        InterviewResponseParseError,
        match="invalid action",
    ):
        parse_interview_action(
            response
        )


def test_parser_rejects_brief_on_question_action() -> None:
    """
    A follow-up question must not prematurely include a brief.
    """
    response = json.dumps(
        {
            "action": "ask_question",
            "question": (
                "Should the playlist build in energy?"
            ),
            "reasoning_summary": (
                "The energy progression is unclear."
            ),
            "brief": valid_brief_data(),
        }
    )

    with pytest.raises(
        InterviewResponseParseError,
        match="invalid action",
    ):
        parse_interview_action(
            response
        )