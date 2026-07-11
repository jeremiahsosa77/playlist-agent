"""Tests for interview response parsing."""

import pytest

from app.conversation import (
    InterviewActionType,
    InterviewResponseParseError,
    parse_interview_action,
)


def test_parser_accepts_question_action() -> None:
    """
    Valid question JSON should become an InterviewAction.
    """
    action = parse_interview_action(
        """
        {
          "action": "ask_question",
          "question": "Popular songs or hidden gems?",
          "reasoning_summary": "Discovery preference is missing."
        }
        """
    )

    assert action.action == (
        InterviewActionType.ASK_QUESTION
    )
    assert action.question == (
        "Popular songs or hidden gems?"
    )


def test_parser_accepts_ready_action() -> None:
    """
    Ready JSON should validate without a question.
    """
    action = parse_interview_action(
        """
        {
          "action": "ready_to_generate",
          "question": null,
          "reasoning_summary": "Enough context exists."
        }
        """
    )

    assert action.action == (
        InterviewActionType.READY_TO_GENERATE
    )
    assert action.question is None


def test_parser_removes_markdown_fences() -> None:
    """
    Common JSON fences should be tolerated.
    """
    action = parse_interview_action(
        """```json
        {
          "action": "clarify",
          "question": "What activity is this for?"
        }
        ```"""
    )

    assert action.action == (
        InterviewActionType.CLARIFY
    )


def test_parser_rejects_invalid_json() -> None:
    """
    Non-JSON responses should fail clearly.
    """
    with pytest.raises(
        InterviewResponseParseError,
        match="not valid JSON",
    ):
        parse_interview_action(
            "Ask them what music they like."
        )


def test_parser_rejects_unknown_action() -> None:
    """
    Unsupported action names should fail validation.
    """
    with pytest.raises(
        InterviewResponseParseError,
        match="invalid action",
    ):
        parse_interview_action(
            """
            {
              "action": "generate_songs",
              "question": null
            }
            """
        )


def test_parser_rejects_missing_question() -> None:
    """
    Question actions must include question text.
    """
    with pytest.raises(
        InterviewResponseParseError,
        match="invalid action",
    ):
        parse_interview_action(
            """
            {
              "action": "ask_question"
            }
            """
        )