"""Tests for the interview decision provider."""

import pytest

from app.conversation import (
    ConversationMessage,
    ConversationRole,
    ConversationSession,
    GeneratedTextInterviewProvider,
    InterviewActionType,
    InterviewProviderError,
)


def build_session() -> ConversationSession:
    """
    Build a short interview session for provider tests.
    """
    return ConversationSession(
        messages=[
            ConversationMessage(
                role=ConversationRole.ASSISTANT,
                content=(
                    "What are we making this playlist for?"
                ),
            ),
            ConversationMessage(
                role=ConversationRole.USER,
                content="A late-night drive.",
            ),
        ],
        question_count=1,
    )


def test_provider_builds_prompt_and_parses_response() -> None:
    """
    The provider should send conversation history to its generator.
    """
    received_prompts: list[str] = []

    def fake_generator(
        prompt: str,
    ) -> str:
        received_prompts.append(
            prompt
        )

        return """
        {
          "action": "ask_question",
          "question": "Popular songs or hidden gems?",
          "reasoning_summary": "Discovery preference is missing."
        }
        """

    provider = GeneratedTextInterviewProvider(
        text_generator=fake_generator
    )

    action = provider.decide(
        build_session()
    )

    assert len(received_prompts) == 1
    assert "A late-night drive." in (
        received_prompts[0]
    )
    assert "Questions already asked: 1" in (
        received_prompts[0]
    )
    assert action.action == (
        InterviewActionType.ASK_QUESTION
    )


def test_provider_returns_ready_action() -> None:
    """
    A valid ready response should include its playlist brief.
    """
    provider = GeneratedTextInterviewProvider(
        text_generator=lambda prompt: """
        {
          "action": "ready_to_generate",
          "question": null,
          "reasoning_summary": "Enough context exists.",
          "brief": {
            "version": "playlist-brief-v1",
            "situation": "A late-night drive.",
            "mood": [
              "energetic",
              "confident"
            ],
            "energy": "high",
            "energy_curve": "Maintain high energy.",
            "preferred_artists": [],
            "preferred_genres": [
              "alternative R&B"
            ],
            "avoid_artists": [],
            "avoid_genres": [],
            "avoid_other": [],
            "familiarity": "balanced",
            "explicit_content": null,
            "playlist_length": 20,
            "is_public": false,
            "additional_notes": null
          }
        }
        """
    )

    action = provider.decide(
        build_session()
    )

    assert (
        action.action
        == InterviewActionType.READY_TO_GENERATE
    )
    assert action.brief is not None
    assert action.brief.situation == (
        "A late-night drive."
    )


def test_provider_wraps_parse_failure() -> None:
    """
    Invalid model output should become a provider-level error.
    """
    provider = GeneratedTextInterviewProvider(
        text_generator=lambda prompt: (
            "This is not JSON."
        )
    )

    with pytest.raises(
        InterviewProviderError,
        match="invalid response",
    ):
        provider.decide(
            build_session()
        )