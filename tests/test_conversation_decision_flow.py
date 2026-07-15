"""Tests for AI-driven conversation service behavior."""

import pytest

from app.conversation import (
    ConversationProviderNotConfiguredError,
    ConversationService,
    ConversationStatus,
    GeneratedTextInterviewProvider,
    InMemoryConversationSessionStore,
    InterviewActionType,
)


def build_service(
    response_text: str,
    max_questions: int = 6,
) -> ConversationService:
    """
    Create a service backed by a predictable fake model response.
    """
    provider = GeneratedTextInterviewProvider(
        text_generator=lambda prompt: response_text,
        max_questions=max_questions,
    )

    return ConversationService(
        session_store=(
            InMemoryConversationSessionStore()
        ),
        decision_provider=provider,
        max_questions=max_questions,
    )


def test_user_response_triggers_follow_up_question() -> None:
    """
    The complete decision flow should add the model's next question.
    """
    service = build_service(
        """
        {
          "action": "ask_question",
          "question": "Do you want familiar songs or hidden gems?",
          "reasoning_summary": "Discovery preference is missing."
        }
        """
    )

    session = service.start_session()

    updated_session, action = (
        service.respond_to_user(
            session.id,
            "A late-night drive.",
        )
    )

    assert action.action == (
        InterviewActionType.ASK_QUESTION
    )
    assert updated_session.status == (
        ConversationStatus.ACTIVE
    )
    assert updated_session.question_count == 2
    assert updated_session.user_message_count == 1
    assert updated_session.messages[-1].content == (
        "Do you want familiar songs or hidden gems?"
    )


def test_user_response_can_finish_interview() -> None:
    """
    The model may mark a detailed interview as ready with a brief.
    """
    service = build_service(
        """
        {
          "action": "ready_to_generate",
          "question": null,
          "reasoning_summary": "The user provided enough context.",
          "brief": {
            "version": "playlist-brief-v1",
            "situation": "A high-energy late-night drive.",
            "mood": [
              "energetic",
              "confident"
            ],
            "energy": "high",
            "energy_curve": "Maintain strong energy.",
            "preferred_artists": [],
            "preferred_genres": [
              "alternative R&B"
            ],
            "avoid_artists": [],
            "avoid_genres": [],
            "avoid_other": [],
            "familiarity": "mostly hidden gems",
            "explicit_content": null,
            "playlist_length": 20,
            "is_public": false,
            "additional_notes": null
          }
        }
        """
    )

    session = service.start_session()

    updated_session, action = (
        service.respond_to_user(
            session.id,
            (
                "A high-energy late-night drive playlist "
                "with mostly hidden alternative R&B songs."
            ),
        )
    )

    assert (
        updated_session.status
        == ConversationStatus.READY_TO_GENERATE
    )

    assert (
        action.action
        == InterviewActionType.READY_TO_GENERATE
    )

    assert action.brief is not None
    assert action.brief.energy == "high"


def test_max_question_limit_forces_readiness() -> None:
    """
    The service must stop interviewing at its configured limit.
    """
    provider_call_count = 0

    def fake_generator(
        prompt: str,
    ) -> str:
        nonlocal provider_call_count
        provider_call_count += 1

        return """
        {
          "action": "ask_question",
          "question": "Another question?"
        }
        """

    provider = GeneratedTextInterviewProvider(
        text_generator=fake_generator,
        max_questions=1,
    )

    service = ConversationService(
        session_store=(
            InMemoryConversationSessionStore()
        ),
        decision_provider=provider,
        max_questions=1,
    )

    session = service.start_session()

    updated_session, action = (
        service.respond_to_user(
            session.id,
            "A road-trip playlist.",
        )
    )

    assert provider_call_count == 0
    assert action.action == (
        InterviewActionType.READY_TO_GENERATE
    )
    assert updated_session.status == (
        ConversationStatus.READY_TO_GENERATE
    )


def test_decision_flow_requires_provider() -> None:
    """
    AI decision-making should fail clearly without a configured provider.
    """
    service = ConversationService(
        session_store=(
            InMemoryConversationSessionStore()
        ),
        decision_provider=None,
        max_questions=6,
    )

    session = service.start_session()

    with pytest.raises(
        ConversationProviderNotConfiguredError,
        match="No interview decision provider",
    ):
        service.respond_to_user(
            session.id,
            "A workout playlist.",
        )