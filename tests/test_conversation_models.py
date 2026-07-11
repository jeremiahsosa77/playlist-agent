"""Tests for conversation domain models."""

import pytest
from pydantic import ValidationError

from app.conversation import (
    ConversationMessage,
    ConversationRole,
    ConversationSession,
    InterviewAction,
    InterviewActionType,
)


def test_conversation_message_accepts_valid_content() -> None:
    """
    A valid conversation message should preserve its role and content.
    """
    message = ConversationMessage(
        role=ConversationRole.USER,
        content="I want music for a late-night drive.",
    )

    assert message.role == ConversationRole.USER
    assert message.content == (
        "I want music for a late-night drive."
    )
    assert message.id
    assert message.created_at


def test_conversation_message_rejects_blank_content() -> None:
    """
    Messages must contain meaningful content.
    """
    with pytest.raises(ValidationError):
        ConversationMessage(
            role=ConversationRole.USER,
            content="",
        )


def test_question_action_requires_question() -> None:
    """
    Question actions must include question text.
    """
    with pytest.raises(
        ValidationError,
        match="must include a question",
    ):
        InterviewAction(
            action=(
                InterviewActionType.ASK_QUESTION
            )
        )


def test_ready_action_rejects_question() -> None:
    """
    A ready-to-generate action must not ask another question.
    """
    with pytest.raises(
        ValidationError,
        match="cannot include a question",
    ):
        InterviewAction(
            action=(
                InterviewActionType.READY_TO_GENERATE
            ),
            question="Anything else?",
        )


def test_session_counts_message_roles() -> None:
    """
    Session properties should calculate message counts correctly.
    """
    session = ConversationSession(
        messages=[
            ConversationMessage(
                role=ConversationRole.ASSISTANT,
                content="What is the occasion?",
            ),
            ConversationMessage(
                role=ConversationRole.USER,
                content="A road trip.",
            ),
            ConversationMessage(
                role=ConversationRole.ASSISTANT,
                content="Daytime or late-night?",
            ),
        ]
    )

    assert session.user_message_count == 1
    assert session.assistant_message_count == 2
    assert session.total_turn_count == 1