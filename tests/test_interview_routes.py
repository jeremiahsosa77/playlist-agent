"""Tests for adaptive interview API routes."""

from fastapi.testclient import TestClient


def create_interview(
    client: TestClient,
) -> dict:
    """
    Create and return one test interview response.
    """
    response = client.post(
        "/api/interviews",
        json={},
    )

    assert response.status_code == 201

    return response.json()


def test_create_interview_returns_opening_question(
    client: TestClient,
) -> None:
    """
    A new interview should begin with one assistant message.
    """
    data = create_interview(
        client
    )

    session = data["session"]

    assert session["status"] == "active"
    assert session["questionCount"] == 1
    assert session["userMessageCount"] == 0
    assert len(session["messages"]) == 1

    opening_message = session["messages"][0]

    assert opening_message["role"] == "assistant"
    assert opening_message["content"] == (
        "What are we making this playlist for?"
    )


def test_create_interview_accepts_custom_opening_question(
    client: TestClient,
) -> None:
    """
    A custom opening question may be supplied.
    """
    response = client.post(
        "/api/interviews",
        json={
            "openingQuestion": (
                "What kind of moment are we "
                "soundtracking?"
            )
        },
    )

    assert response.status_code == 201

    message = response.json()[
        "session"
    ]["messages"][0]

    assert message["content"] == (
        "What kind of moment are we soundtracking?"
    )


def test_get_interview_returns_current_state(
    client: TestClient,
) -> None:
    """
    A created interview should be retrievable by ID.
    """
    created = create_interview(
        client
    )
    session_id = created["session"]["id"]

    response = client.get(
        f"/api/interviews/{session_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == session_id


def test_submit_message_returns_follow_up_question(
    client: TestClient,
) -> None:
    """
    A normal user response should trigger the fake provider question.
    """
    created = create_interview(
        client
    )
    session_id = created["session"]["id"]

    response = client.post(
        (
            f"/api/interviews/{session_id}"
            "/messages"
        ),
        json={
            "content": "A late-night drive."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"]["action"] == (
        "ask_question"
    )
    assert data["action"]["question"] == (
        "Do you want familiar songs or hidden gems?"
    )
    assert data["session"]["questionCount"] == 2
    assert data["session"]["userMessageCount"] == 1
    assert data["session"]["status"] == "active"


def test_submit_message_can_finish_interview(
    client: TestClient,
) -> None:
    """
    A sufficiently detailed response may finish the interview.
    """
    created = create_interview(
        client
    )
    session_id = created["session"]["id"]

    response = client.post(
        (
            f"/api/interviews/{session_id}"
            "/messages"
        ),
        json={
            "content": (
                "I am ready now with a detailed "
                "late-night R&B request."
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"]["action"] == (
        "ready_to_generate"
    )
    assert data["action"]["question"] is None
    assert data["session"]["status"] == (
        "ready_to_generate"
    )


def test_ready_interview_rejects_more_messages(
    client: TestClient,
) -> None:
    """
    A ready session must reject additional interview messages.
    """
    created = create_interview(
        client
    )
    session_id = created["session"]["id"]

    client.post(
        (
            f"/api/interviews/{session_id}"
            "/messages"
        ),
        json={
            "content": "I am ready now."
        },
    )

    response = client.post(
        (
            f"/api/interviews/{session_id}"
            "/messages"
        ),
        json={
            "content": "One more preference."
        },
    )

    assert response.status_code == 409

    error = response.json()["error"]

    assert error["code"] == (
        "INTERVIEW_STATE_CONFLICT"
    )


def test_cancel_interview_changes_status(
    client: TestClient,
) -> None:
    """
    An active interview should support cancellation.
    """
    created = create_interview(
        client
    )
    session_id = created["session"]["id"]

    response = client.post(
        (
            f"/api/interviews/{session_id}"
            "/cancel"
        )
    )

    assert response.status_code == 200
    assert response.json()[
        "session"
    ]["status"] == "cancelled"


def test_unknown_interview_returns_404(
    client: TestClient,
) -> None:
    """
    Unknown session IDs should return the structured 404 response.
    """
    response = client.get(
        "/api/interviews/missing-session"
    )

    assert response.status_code == 404

    error = response.json()["error"]

    assert error["code"] == (
        "INTERVIEW_SESSION_NOT_FOUND"
    )


def test_blank_message_returns_validation_error(
    client: TestClient,
) -> None:
    """
    Blank user responses should fail request validation.
    """
    created = create_interview(
        client
    )
    session_id = created["session"]["id"]

    response = client.post(
        (
            f"/api/interviews/{session_id}"
            "/messages"
        ),
        json={
            "content": ""
        },
    )

    assert response.status_code == 422
    assert response.json()[
        "error"
    ]["code"] == "REQUEST_VALIDATION_ERROR"


def test_delete_interview_removes_session(
    client: TestClient,
) -> None:
    """
    Deleted interviews should no longer be retrievable.
    """
    created = create_interview(
        client
    )
    session_id = created["session"]["id"]

    delete_response = client.delete(
        f"/api/interviews/{session_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/interviews/{session_id}"
    )

    assert get_response.status_code == 404