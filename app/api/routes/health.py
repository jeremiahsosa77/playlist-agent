"""API health-check route."""

from fastapi import APIRouter

from app.config import (
    APP_ENVIRONMENT,
    APP_NAME,
    APP_VERSION,
)
from app.schemas import HealthResponse


router = APIRouter(
    tags=["Health"],
)


@router.get(
    "/health",
    response_model=HealthResponse,
)
def get_health() -> HealthResponse:
    """
    Return the current API health status.
    """
    return HealthResponse(
        status="healthy",
        application=APP_NAME,
        version=APP_VERSION,
        environment=APP_ENVIRONMENT,
    )