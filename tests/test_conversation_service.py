"""Tests for the conversation application service."""

import pytest

from app.conversation import (
    ConversationRole,
    ConversationService,
    ConversationStateError,
    ConversationStatus,
    InMemoryConversationSessionStore,
    InterviewAction,
    InterviewActionType,
)


def build_service() -> ConversationService:
    """
    Return a conversation service with isolated storage.
    """
    return ConversationService(
        session_store=(
            InMemoryConversationSessionStore()
        )
    )


def test_start_session_adds_opening_question() -> None:
    """
    Starting an interview should create one assistant question.
    """
    service = build_service()

    session = service.start_session()

    assert session.status == (
        ConversationStatus.ACTIVE
    )
    assert session.question_count == 1
    assert len(session.messages) == 1
    assert session.messages[0].role == (
        ConversationRole.ASSISTANT
    )
    assert session.messages[0].content == (
        "What are we making this playlist for?"
    )


def test_add_user_message_updates_session() -> None:
    """
    Active sessions should accept user responses.
    """
    service = build_service()
    session = service.start_session()

    updated = service.add_user_message(
        session.id,
        "A late-night drive.",
    )

    assert updated.user_message_count == 1
    assert updated.messages[-1].role == (
        ConversationRole.USER
    )
    assert updated.messages[-1].content == (
        "A late-night drive."
    )


def test_apply_question_action_adds_assistant_message() -> None:
    """
    Ask-question actions should add a new assistant question.
    """
    service = build_service()
    session = service.start_session()

    service.add_user_message(
        session.id,
        "A road trip.",
    )

    updated = service.apply_action(
        session.id,
        InterviewAction(
            action=(
                InterviewActionType.ASK_QUESTION
            ),
            question=(
                "Should the playlist feel energetic "
                "or relaxed?"
            ),
        ),
    )

    assert updated.question_count == 2
    assert updated.messages[-1].role == (
        ConversationRole.ASSISTANT
    )


def test_apply_clarification_tracks_clarification_count() -> None:
    """
    Clarification actions should be tracked separately.
    """
    service = build_service()
    session = service.start_session()

    service.add_user_message(
        session.id,
        "I don't know.",
    )

    updated = service.apply_action(
        session.id,
        InterviewAction(
            action=InterviewActionType.CLARIFY,
            question=(
                "What will you be doing while listening?"
            ),
        ),
    )

    assert updated.question_count == 2
    assert updated.clarification_count == 1


def test_ready_action_changes_session_status() -> None:
    """
    Ready actions should stop the interview question loop.
    """
    service = build_service()
    session = service.start_session()

    service.add_user_message(
        session.id,
        "Late-night driving with hidden gems.",
    )

    updated = service.apply_action(
        session.id,
        InterviewAction(
            action=(
                InterviewActionType.READY_TO_GENERATE
            )
        ),
    )

    assert updated.status == (
        ConversationStatus.READY_TO_GENERATE
    )


def test_ready_session_rejects_more_user_messages() -> None:
    """
    A closed interview should not accept another response.
    """
    service = build_service()
    session = service.start_session()

    service.apply_action(
        session.id,
        InterviewAction(
            action=(
                InterviewActionType.READY_TO_GENERATE
            )
        ),
    )

    with pytest.raises(
        ConversationStateError,
        match="not active",
    ):
        service.add_user_message(
            session.id,
            "One more thing.",
        )


def test_ready_session_can_be_completed() -> None:
    """
    Playlist generation may mark a ready session as completed.
    """
    service = build_service()
    session = service.start_session()

    service.apply_action(
        session.id,
        InterviewAction(
            action=(
                InterviewActionType.READY_TO_GENERATE
            )
        ),
    )

    completed = service.mark_completed(
        session.id
    )

    assert completed.status == (
        ConversationStatus.COMPLETED
    )


def test_active_session_cannot_be_completed() -> None:
    """
    Completion should require a ready-to-generate decision.
    """
    service = build_service()
    session = service.start_session()

    with pytest.raises(
        ConversationStateError,
        match="ready-to-generate",
    ):
        service.mark_completed(
            session.id
        )


def test_session_can_be_cancelled() -> None:
    """
    Active sessions should support explicit cancellation.
    """
    service = build_service()
    session = service.start_session()

    cancelled = service.cancel_session(
        session.id
    )

    assert cancelled.status == (
        ConversationStatus.CANCELLED
    )