"""FastAPI application entry point for Playlist Agent."""

import hmac
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.errors import register_exception_handlers
from app.api.routes import (
    configuration_router,
    health_router,
    interviews_router,
    playlists_router,
)
from app.config import (
    API_PREFIX,
    APP_NAME,
    APP_VERSION,
    get_cors_origins,
)


PROTECTED_API_PATHS = (
    "/api/interviews",
    "/api/playlists",
)


def requires_internal_key(
    path: str,
) -> bool:
    """
    Return whether a route requires the private Vercel-to-Render key.
    """
    return any(
        path.startswith(prefix)
        for prefix in PROTECTED_API_PATHS
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

    @application.middleware("http")
    async def require_internal_api_key(
        request: Request,
        call_next,
    ):
        """
        Protect generation and interview endpoints in production.

        When INTERNAL_API_KEY is not configured, protection is disabled
        so normal local development and automated tests still work.
        """
        expected_key = os.getenv(
            "INTERNAL_API_KEY",
            "",
        ).strip()

        if (
            expected_key
            and requires_internal_key(
                request.url.path
            )
        ):
            provided_key = request.headers.get(
                "X-Playlist-Agent-Key",
                "",
            )

            if not hmac.compare_digest(
                provided_key,
                expected_key,
            ):
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": {
                            "code": "UNAUTHORIZED",
                            "message": (
                                "A valid internal API key "
                                "is required."
                            ),
                        }
                    },
                )

        return await call_next(request)

    application.include_router(
        health_router,
        prefix=API_PREFIX,
    )
    application.include_router(
        configuration_router,
        prefix=API_PREFIX,
    )
    application.include_router(
        interviews_router,
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