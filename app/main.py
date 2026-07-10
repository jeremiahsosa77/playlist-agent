"""FastAPI application entry point for Playlist Agent."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes import (
    configuration_router,
    health_router,
    playlists_router,
)
from app.config import (
    API_PREFIX,
    APP_NAME,
    APP_VERSION,
    get_cors_origins,
)


def create_application() -> FastAPI:
    """
    Create and configure the Playlist Agent API.
    """
    application = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description=(
            "Conversational AI playlist generation, Spotify enrichment, "
            "quality evaluation, and publishing API."
        ),
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(
        health_router,
        prefix=API_PREFIX,
    )
    application.include_router(
        configuration_router,
        prefix=API_PREFIX,
    )
    application.include_router(
        playlists_router,
        prefix=API_PREFIX,
    )

    register_exception_handlers(
        application
    )

    return application


app = create_application()