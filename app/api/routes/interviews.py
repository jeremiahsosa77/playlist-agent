"""Adaptive playlist interview API routes."""

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)

from app.api.dependencies import (
    get_conversation_service,
)
from app.conversation import (
    ConversationService,
)
from app.schemas import (
    CancelInterviewResponse,
    CreateInterviewRequest,
    CreateInterviewResponse,
    InterviewActionResponse,
    InterviewSessionResponse,
    SubmitInterviewMessageRequest,
    SubmitInterviewMessageResponse,
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
)


@router.post(
    "",
    response_model=CreateInterviewResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(
    request: CreateInterviewRequest,
    conversation_service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> CreateInterviewResponse:
    """
    Start a new adaptive playlist interview.
    """
    if request.opening_question:
        session = conversation_service.start_session(
            opening_question=(
                request.opening_question
            )
        )
    else:
        session = (
            conversation_service.start_session()
        )

    return CreateInterviewResponse(
        session=InterviewSessionResponse.from_domain(
            session
        )
    )


@router.get(
    "/{session_id}",
    response_model=InterviewSessionResponse,
    response_model_by_alias=True,
)
def get_interview(
    session_id: str,
    conversation_service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> InterviewSessionResponse:
    """
    Return the current state of an interview session.
    """
    session = conversation_service.get_session(
        session_id
    )

    return InterviewSessionResponse.from_domain(
        session
    )


@router.post(
    "/{session_id}/messages",
    response_model=SubmitInterviewMessageResponse,
    response_model_by_alias=True,
)
def submit_interview_message(
    session_id: str,
    request: SubmitInterviewMessageRequest,
    conversation_service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> SubmitInterviewMessageResponse:
    """
    Submit one user response and receive the next AI action.
    """
    session, action = (
        conversation_service.respond_to_user(
            session_id=session_id,
            content=request.content,
        )
    )

    return SubmitInterviewMessageResponse(
        session=InterviewSessionResponse.from_domain(
            session
        ),
        action=InterviewActionResponse.from_domain(
            action
        ),
    )


@router.post(
    "/{session_id}/cancel",
    response_model=CancelInterviewResponse,
    response_model_by_alias=True,
)
def cancel_interview(
    session_id: str,
    conversation_service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> CancelInterviewResponse:
    """
    Cancel an interview session.
    """
    session = (
        conversation_service.cancel_session(
            session_id
        )
    )

    return CancelInterviewResponse(
        session=InterviewSessionResponse.from_domain(
            session
        )
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_interview(
    session_id: str,
    conversation_service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> Response:
    """
    Delete an interview session from temporary storage.

    This endpoint is mainly useful during development and testing.
    """
    conversation_service.delete_session(
        session_id
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )