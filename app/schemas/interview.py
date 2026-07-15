"""Public API schemas for adaptive playlist interviews."""

from datetime import datetime

from pydantic import Field

from app.conversation import (
    ConversationMessage,
    ConversationSession,
    InterviewAction,
    PlaylistBrief,
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


class PlaylistBriefResponse(APIModel):
    """
    Structured playlist requirements gathered by the interview.
    """

    version: str
    situation: str
    mood: list[str]
    energy: str | None
    energy_curve: str | None
    preferred_artists: list[str]
    preferred_genres: list[str]
    avoid_artists: list[str]
    avoid_genres: list[str]
    avoid_other: list[str]
    familiarity: str | None
    explicit_content: bool | None
    playlist_length: int
    is_public: bool
    additional_notes: str | None

    @classmethod
    def from_domain(
        cls,
        brief: PlaylistBrief,
    ) -> "PlaylistBriefResponse":
        """
        Convert a domain playlist brief into an API response.
        """
        return cls(
            version=brief.version,
            situation=brief.situation,
            mood=brief.mood,
            energy=brief.energy,
            energy_curve=brief.energy_curve,
            preferred_artists=brief.preferred_artists,
            preferred_genres=brief.preferred_genres,
            avoid_artists=brief.avoid_artists,
            avoid_genres=brief.avoid_genres,
            avoid_other=brief.avoid_other,
            familiarity=brief.familiarity,
            explicit_content=brief.explicit_content,
            playlist_length=brief.playlist_length,
            is_public=brief.is_public,
            additional_notes=brief.additional_notes,
        )


class InterviewActionResponse(APIModel):
    """
    Structured action selected by the interview decision engine.
    """

    action: InterviewActionType

    question: str | None = None

    reasoning_summary: str | None = None

    brief: PlaylistBriefResponse | None = None

    @classmethod
    def from_domain(
        cls,
        action: InterviewAction,
    ) -> "InterviewActionResponse":
        """
        Convert a domain action into a public API response.
        """
        return cls(
            action=action.action,
            question=action.question,
            reasoning_summary=action.reasoning_summary,
            brief=(
                PlaylistBriefResponse.from_domain(
                    action.brief
                )
                if action.brief is not None
                else None
            ),
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