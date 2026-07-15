"""Conversation domain models."""

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.conversation.state import (
    ConversationRole,
    ConversationStatus,
    InterviewActionType,
)


PLAYLIST_BRIEF_VERSION = "playlist-brief-v1"


def utc_now() -> datetime:
    """
    Return the current timezone-aware UTC datetime.
    """
    return datetime.now(UTC)


class ConversationModel(BaseModel):
    """
    Base configuration for conversation domain models.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class PlaylistBrief(ConversationModel):
    """
    Structured playlist requirements collected during an interview.

    This object becomes the stable contract between the interview,
    playlist generation, evaluation, and future repair systems.
    """

    version: str = Field(
        default=PLAYLIST_BRIEF_VERSION,
        min_length=1,
        max_length=100,
    )

    situation: str = Field(
        min_length=1,
        max_length=2000,
    )

    mood: list[str] = Field(
        default_factory=list,
        max_length=12,
    )

    energy: str | None = Field(
        default=None,
        max_length=500,
    )

    energy_curve: str | None = Field(
        default=None,
        max_length=1000,
    )

    preferred_artists: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    preferred_genres: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    avoid_artists: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    avoid_genres: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    avoid_other: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    familiarity: str | None = Field(
        default=None,
        max_length=500,
    )

    explicit_content: bool | None = None

    playlist_length: int = Field(
        default=20,
        ge=5,
        le=100,
    )

    is_public: bool = False

    additional_notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class ConversationMessage(ConversationModel):
    """
    One message in an interview conversation.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    role: ConversationRole

    content: str = Field(
        min_length=1,
        max_length=4000,
    )

    created_at: datetime = Field(
        default_factory=utc_now
    )


class InterviewAction(ConversationModel):
    """
    Structured result produced by the interview decision engine.
    """

    action: InterviewActionType

    question: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )

    reasoning_summary: str | None = Field(
        default=None,
        max_length=2000,
    )

    brief: PlaylistBrief | None = None

    @model_validator(mode="after")
    def validate_action_fields(
        self,
    ) -> "InterviewAction":
        """
        Validate the fields allowed for each interview action.
        """
        asks_question = self.action in {
            InterviewActionType.ASK_QUESTION,
            InterviewActionType.CLARIFY,
        }

        if asks_question and not self.question:
            raise ValueError(
                "Question actions must include a question."
            )

        if asks_question and self.brief is not None:
            raise ValueError(
                "Question actions cannot include a playlist brief."
            )

        if (
            self.action
            == InterviewActionType.READY_TO_GENERATE
            and self.question is not None
        ):
            raise ValueError(
                "A ready-to-generate action cannot include a question."
            )

        return self


class ConversationSession(ConversationModel):
    """
    Complete state for one adaptive playlist interview.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    status: ConversationStatus = (
        ConversationStatus.ACTIVE
    )

    messages: list[ConversationMessage] = Field(
        default_factory=list
    )

    question_count: int = Field(
        default=0,
        ge=0,
    )

    clarification_count: int = Field(
        default=0,
        ge=0,
    )

    created_at: datetime = Field(
        default_factory=utc_now
    )

    updated_at: datetime = Field(
        default_factory=utc_now
    )

    @property
    def user_message_count(self) -> int:
        """
        Return the number of user messages in the session.
        """
        return sum(
            message.role == ConversationRole.USER
            for message in self.messages
        )

    @property
    def assistant_message_count(self) -> int:
        """
        Return the number of assistant messages in the session.
        """
        return sum(
            message.role
            == ConversationRole.ASSISTANT
            for message in self.messages
        )

    @property
    def total_turn_count(self) -> int:
        """
        Return the number of user messages submitted so far.
        """
        return self.user_message_count

    @property
    def is_active(self) -> bool:
        """
        Return whether the interview may accept another user message.
        """
        return self.status == ConversationStatus.ACTIVE