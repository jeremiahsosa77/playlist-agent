"""Tests for parsing adaptive interview model responses."""

import json

import pytest

from app.conversation import (
    PLAYLIST_BRIEF_VERSION,
    InterviewActionType,
    InterviewResponseParseError,
    parse_interview_action,
)


def build_valid_brief() -> dict[str, object]:
    """
    Return one valid structured playlist brief.
    """
    return {
        "version": PLAYLIST_BRIEF_VERSION,
        "situation": (
            "A high-energy late-night drive."
        ),
        "mood": [
            "energetic",
            "confident",
        ],
        "energy": "high",
        "energy_curve": (
            "Maintain strong energy throughout."
        ),
        "preferred_artists": [],
        "preferred_genres": [
            "alternative R&B",
        ],
        "avoid_artists": [],
        "avoid_genres": [],
        "avoid_other": [],
        "familiarity": "mostly hidden gems",
        "explicit_content": None,
        "playlist_length": 20,
        "is_public": False,
        "additional_notes": None,
    }


def test_parser_accepts_question_action() -> None:
    """
    Question JSON should produce an ask-question action.
    """
    action = parse_interview_action(
        """
        {
          "action": "ask_question",
          "question": "Should the playlist build in energy?",
          "reasoning_summary": "The energy progression is unclear.",
          "brief": null
        }
        """
    )

    assert (
        action.action
        == InterviewActionType.ASK_QUESTION
    )
    assert action.question == (
        "Should the playlist build in energy?"
    )
    assert action.brief is None


def test_parser_accepts_ready_action() -> None:
    """
    Ready JSON should validate with a complete brief.
    """
    action = parse_interview_action(
        json.dumps(
            {
                "action": "ready_to_generate",
                "question": None,
                "reasoning_summary": (
                    "Enough context exists."
                ),
                "brief": build_valid_brief(),
            }
        )
    )

    assert (
        action.action
        == InterviewActionType.READY_TO_GENERATE
    )
    assert action.question is None
    assert action.brief is not None
    assert action.brief.playlist_length == 20


def test_parser_removes_markdown_json_fences() -> None:
    """
    JSON Markdown fences should be tolerated.
    """
    action = parse_interview_action(
        """
        ```json
        {
          "action": "clarify",
          "question": "Do you mean upbeat or intense?",
          "reasoning_summary": "The word energetic is ambiguous.",
          "brief": null
        }
        ```
        """
    )

    assert (
        action.action
        == InterviewActionType.CLARIFY
    )


def test_parser_rejects_invalid_json() -> None:
    """
    Non-JSON model output should fail clearly.
    """
    with pytest.raises(
        InterviewResponseParseError,
        match="not valid JSON",
    ):
        parse_interview_action(
            "Ask the user about energy."
        )


def test_parser_rejects_non_object_json() -> None:
    """
    The top-level model output must be an object.
    """
    with pytest.raises(
        InterviewResponseParseError,
        match="must be a JSON object",
    ):
        parse_interview_action(
            '["ask_question"]'
        )


def test_parser_rejects_invalid_action_shape() -> None:
    """
    Responses missing required action fields should fail.
    """
    with pytest.raises(
        InterviewResponseParseError,
        match="invalid action",
    ):
        parse_interview_action(
            """
            {
              "action": "ask_question",
              "question": null,
              "brief": null
            }
            """
        )


def test_parser_rejects_empty_response() -> None:
    """
    Empty provider output should fail.
    """
    with pytest.raises(
        InterviewResponseParseError,
        match="empty response",
    ):
        parse_interview_action("")