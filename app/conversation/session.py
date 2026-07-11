"""Conversation session storage."""

from threading import RLock

from app.conversation.models import ConversationSession


class ConversationSessionNotFoundError(
    LookupError
):
    """
    Raised when a requested conversation session does not exist.
    """


class InMemoryConversationSessionStore:
    """
    Thread-safe in-memory storage for conversation sessions.

    This is appropriate for the current development phase. The interface
    can later be implemented with PostgreSQL or Redis without changing
    the conversation service.
    """

    def __init__(self) -> None:
        self._sessions: dict[
            str,
            ConversationSession,
        ] = {}
        self._lock = RLock()

    def create(
        self,
        session: ConversationSession,
    ) -> ConversationSession:
        """
        Store and return a new conversation session.
        """
        with self._lock:
            if session.id in self._sessions:
                raise ValueError(
                    "A conversation session with this ID "
                    "already exists."
                )

            stored_session = session.model_copy(
                deep=True
            )

            self._sessions[
                session.id
            ] = stored_session

            return stored_session.model_copy(
                deep=True
            )

    def get(
        self,
        session_id: str,
    ) -> ConversationSession:
        """
        Return one session by ID.
        """
        with self._lock:
            session = self._sessions.get(
                session_id
            )

            if session is None:
                raise ConversationSessionNotFoundError(
                    "Conversation session was not found."
                )

            return session.model_copy(
                deep=True
            )

    def save(
        self,
        session: ConversationSession,
    ) -> ConversationSession:
        """
        Replace a previously stored session.
        """
        with self._lock:
            if session.id not in self._sessions:
                raise ConversationSessionNotFoundError(
                    "Conversation session was not found."
                )

            stored_session = session.model_copy(
                deep=True
            )

            self._sessions[
                session.id
            ] = stored_session

            return stored_session.model_copy(
                deep=True
            )

    def delete(
        self,
        session_id: str,
    ) -> None:
        """
        Remove a conversation session.
        """
        with self._lock:
            if session_id not in self._sessions:
                raise ConversationSessionNotFoundError(
                    "Conversation session was not found."
                )

            del self._sessions[session_id]

    def count(self) -> int:
        """
        Return the number of stored sessions.
        """
        with self._lock:
            return len(self._sessions)

    def clear(self) -> None:
        """
        Remove every stored session.
        """
        with self._lock:
            self._sessions.clear()