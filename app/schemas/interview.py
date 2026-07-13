"""Public API schemas for adaptive playlist interviews."""

from datetime import datetime

from pydantic import Field

from app.conversation import (
    ConversationMessage,
    ConversationSession,
    InterviewAction,
)
from app.conversation.state import (
    ConversationRole,
    ConversationStatus,
    InterviewActionType,
)
from app.schemas.common import APIModel


class InterviewMessageResponse(APIModel):
    """
    One conversation message returned through the public API.
    """

    id: str
    role: ConversationRole
    content: str
    created_at: datetime

    @classmethod
    def from_domain(
        cls,
        message: ConversationMessage,
    ) -> "InterviewMessageResponse":
        """
        Convert a domain conversation message into an API response.
        """
        return cls(
            id=message.id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )


class InterviewActionResponse(APIModel):
    """
    Structured action selected by the interview decision engine.
    """

    action: InterviewActionType
    question: str | None = None
    reasoning_summary: str | None = None

    @classmethod
    def from_domain(
        cls,
        action: InterviewAction,
    ) -> "InterviewActionResponse":
        """
        Convert a domain action into an API response.
        """
        return cls(
            action=action.action,
            question=action.question,
            reasoning_summary=action.reasoning_summary,
        )


class InterviewSessionResponse(APIModel):
    """
    Complete public state for one playlist interview.
    """

    id: str
    status: ConversationStatus
    messages: list[InterviewMessageResponse]
    question_count: int
    clarification_count: int
    user_message_count: int
    assistant_message_count: int
    total_turn_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(
        cls,
        session: ConversationSession,
    ) -> "InterviewSessionResponse":
        """
        Convert the conversation session domain model to an API response.
        """
        return cls(
            id=session.id,
            status=session.status,
            messages=[
                InterviewMessageResponse.from_domain(
                    message
                )
                for message in session.messages
            ],
            question_count=session.question_count,
            clarification_count=(
                session.clarification_count
            ),
            user_message_count=(
                session.user_message_count
            ),
            assistant_message_count=(
                session.assistant_message_count
            ),
            total_turn_count=(
                session.total_turn_count
            ),
            created_at=session.created_at,
            updated_at=session.updated_at,
        )


class CreateInterviewRequest(APIModel):
    """
    Optional settings supplied when starting an interview.
    """

    opening_question: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )


class CreateInterviewResponse(APIModel):
    """
    Response returned when a new interview session is created.
    """

    session: InterviewSessionResponse


class SubmitInterviewMessageRequest(APIModel):
    """
    One user response submitted to an active interview.
    """

    content: str = Field(
        min_length=1,
        max_length=4000,
    )


class SubmitInterviewMessageResponse(APIModel):
    """
    Updated interview state and the AI-selected action.
    """

    session: InterviewSessionResponse
    action: InterviewActionResponse


class CancelInterviewResponse(APIModel):
    """
    Response returned after cancelling an interview.
    """

    session: InterviewSessionResponse