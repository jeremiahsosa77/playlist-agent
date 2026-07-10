"""Health-check response schemas."""

from app.schemas.common import APIModel


class HealthResponse(APIModel):
    """
    Basic API health status.
    """

    status: str
    application: str
    version: str
    environment: str