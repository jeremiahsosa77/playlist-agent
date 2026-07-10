"""FastAPI route collection."""

from app.api.routes.configuration import (
    router as configuration_router,
)
from app.api.routes.health import router as health_router
from app.api.routes.playlists import router as playlists_router


__all__ = [
    "configuration_router",
    "health_router",
    "playlists_router",
]