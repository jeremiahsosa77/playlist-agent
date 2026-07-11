"""Conversation state and action enumerations."""

from enum import StrEnum


class ConversationRole(StrEnum):
    """
    Supported roles for conversation messages.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(StrEnum):
    """
    Lifecycle states for an interview session.
    """

    ACTIVE = "active"
    READY_TO_GENERATE = "ready_to_generate"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewActionType(StrEnum):
    """
    Structured actions that the interview engine may return.
    """

    ASK_QUESTION = "ask_question"
    CLARIFY = "clarify"
    READY_TO_GENERATE = "ready_to_generate"