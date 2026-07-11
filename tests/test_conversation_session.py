"""Tests for conversation session storage."""

import pytest

from app.conversation import (
    ConversationSession,
    ConversationSessionNotFoundError,
    InMemoryConversationSessionStore,
)


def test_session_store_creates_and_gets_session() -> None:
    """
    A stored session should be retrievable by ID.
    """
    store = InMemoryConversationSessionStore()
    session = ConversationSession()

    created = store.create(
        session
    )
    retrieved = store.get(
        session.id
    )

    assert created == retrieved
    assert store.count() == 1


def test_session_store_returns_deep_copy() -> None:
    """
    Modifying a retrieved session must not silently mutate storage.
    """
    store = InMemoryConversationSessionStore()
    session = ConversationSession()

    store.create(
        session
    )

    retrieved = store.get(
        session.id
    )
    retrieved.question_count = 99

    stored_again = store.get(
        session.id
    )

    assert stored_again.question_count == 0


def test_session_store_saves_changes() -> None:
    """
    Explicitly saved changes should persist.
    """
    store = InMemoryConversationSessionStore()
    session = store.create(
        ConversationSession()
    )

    session.question_count = 3

    store.save(
        session
    )

    assert (
        store.get(
            session.id
        ).question_count
        == 3
    )


def test_session_store_rejects_unknown_session() -> None:
    """
    Unknown session IDs should produce a domain-specific error.
    """
    store = InMemoryConversationSessionStore()

    with pytest.raises(
        ConversationSessionNotFoundError
    ):
        store.get(
            "missing-session"
        )


def test_session_store_deletes_session() -> None:
    """
    Deleted sessions should no longer be retrievable.
    """
    store = InMemoryConversationSessionStore()
    session = store.create(
        ConversationSession()
    )

    store.delete(
        session.id
    )

    assert store.count() == 0

    with pytest.raises(
        ConversationSessionNotFoundError
    ):
        store.get(
            session.id
        )