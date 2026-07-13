"""Conversation session application service."""

from app.conversation.config import (
    INTERVIEW_MAX_QUESTIONS,
)
from app.conversation.models import (
    ConversationMessage,
    ConversationSession,
    InterviewAction,
    utc_now,
)
from app.conversation.provider import (
    InterviewDecisionProvider,
)
from app.conversation.session import (
    InMemoryConversationSessionStore,
)
from app.conversation.state import (
    ConversationRole,
    ConversationStatus,
    InterviewActionType,
)


DEFAULT_OPENING_QUESTION = (
    "What are we making this playlist for?"
)


class ConversationStateError(ValueError):
    """
    Raised when an operation conflicts with the session lifecycle.
    """


class ConversationProviderNotConfiguredError(
    RuntimeError
):
    """
    Raised when AI decision-making is requested without a provider.
    """


class ConversationService:
    """
    Manage adaptive playlist interview sessions.
    """

    def __init__(
        self,
        session_store: (
            InMemoryConversationSessionStore
            | None
        ) = None,
        decision_provider: (
            InterviewDecisionProvider
            | None
        ) = None,
        max_questions: int = INTERVIEW_MAX_QUESTIONS,
    ) -> None:
        self._session_store = (
            session_store
            or InMemoryConversationSessionStore()
        )
        self._decision_provider = decision_provider
        self._max_questions = max_questions

    def start_session(
        self,
        opening_question: str = (
            DEFAULT_OPENING_QUESTION
        ),
    ) -> ConversationSession:
        """
        Create a session and add the first assistant question.
        """
        session = ConversationSession()

        opening_message = ConversationMessage(
            role=ConversationRole.ASSISTANT,
            content=opening_question,
        )

        session.messages.append(
            opening_message
        )
        session.question_count = 1
        session.updated_at = utc_now()

        return self._session_store.create(
            session
        )

    def get_session(
        self,
        session_id: str,
    ) -> ConversationSession:
        """
        Retrieve a conversation session.
        """
        return self._session_store.get(
            session_id
        )
    
    def delete_session(
        self,
        session_id: str,
    ) -> None:
        """
        Permanently remove a conversation session.
        """
        self._session_store.delete(
            session_id
        )

    def add_user_message(
        self,
        session_id: str,
        content: str,
    ) -> ConversationSession:
        """
        Add a user response to an active session.
        """
        session = self._session_store.get(
            session_id
        )

        self._require_active_session(
            session
        )

        session.messages.append(
            ConversationMessage(
                role=ConversationRole.USER,
                content=content,
            )
        )
        session.updated_at = utc_now()

        return self._session_store.save(
            session
        )

    def respond_to_user(
        self,
        session_id: str,
        content: str,
    ) -> tuple[
        ConversationSession,
        InterviewAction,
    ]:
        """
        Add a user response, request the next AI action, and apply it.
        """
        session = self.add_user_message(
            session_id,
            content,
        )

        if (
            session.question_count
            >= self._max_questions
        ):
            action = InterviewAction(
                action=(
                    InterviewActionType.READY_TO_GENERATE
                ),
                reasoning_summary=(
                    "The interview reached its maximum "
                    "question count."
                ),
            )
        else:
            if self._decision_provider is None:
                raise (
                    ConversationProviderNotConfiguredError(
                        "No interview decision provider "
                        "has been configured."
                    )
                )

            action = self._decision_provider.decide(
                session
            )

        updated_session = self.apply_action(
            session.id,
            action,
        )

        return updated_session, action

    def apply_action(
        self,
        session_id: str,
        action: InterviewAction,
    ) -> ConversationSession:
        """
        Apply a structured assistant action to a session.
        """
        session = self._session_store.get(
            session_id
        )

        self._require_active_session(
            session
        )

        if (
            action.action
            == InterviewActionType.READY_TO_GENERATE
        ):
            session.status = (
                ConversationStatus.READY_TO_GENERATE
            )
            session.updated_at = utc_now()

            return self._session_store.save(
                session
            )

        if action.question is None:
            raise ValueError(
                "Question action is missing its question."
            )

        session.messages.append(
            ConversationMessage(
                role=ConversationRole.ASSISTANT,
                content=action.question,
            )
        )

        session.question_count += 1

        if (
            action.action
            == InterviewActionType.CLARIFY
        ):
            session.clarification_count += 1

        session.updated_at = utc_now()

        return self._session_store.save(
            session
        )

    def mark_completed(
        self,
        session_id: str,
    ) -> ConversationSession:
        """
        Mark a ready-to-generate session as completed.
        """
        session = self._session_store.get(
            session_id
        )

        if (
            session.status
            != ConversationStatus.READY_TO_GENERATE
        ):
            raise ConversationStateError(
                "Only a ready-to-generate session "
                "can be completed."
            )

        session.status = (
            ConversationStatus.COMPLETED
        )
        session.updated_at = utc_now()

        return self._session_store.save(
            session
        )

    def cancel_session(
        self,
        session_id: str,
    ) -> ConversationSession:
        """
        Cancel an active or ready-to-generate session.
        """
        session = self._session_store.get(
            session_id
        )

        if session.status in {
            ConversationStatus.COMPLETED,
            ConversationStatus.CANCELLED,
        }:
            raise ConversationStateError(
                "This conversation session is already closed."
            )

        session.status = (
            ConversationStatus.CANCELLED
        )
        session.updated_at = utc_now()

        return self._session_store.save(
            session
        )

    @staticmethod
    def _require_active_session(
        session: ConversationSession,
    ) -> None:
        """
        Ensure a session is accepting interview activity.
        """
        if not session.is_active:
            raise ConversationStateError(
                "The conversation session is not active."
            )