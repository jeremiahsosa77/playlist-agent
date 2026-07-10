"""LLM provider and model configuration routes."""

import os

from fastapi import APIRouter

from app.config import (
    GEMINI_MODEL,
    LLM_PROVIDER,
    OPENROUTER_MODEL,
    get_active_model,
)
from app.schemas import (
    ModelInformation,
    ModelsResponse,
    ProviderInformation,
    ProvidersResponse,
)


router = APIRouter(
    tags=["Configuration"],
)


@router.get(
    "/providers",
    response_model=ProvidersResponse,
)
def get_providers() -> ProvidersResponse:
    """
    Return supported and currently active LLM providers.
    """
    gemini_enabled = bool(
        os.getenv("GEMINI_API_KEY")
    )
    openrouter_enabled = bool(
        os.getenv("OPENROUTER_API_KEY")
    )

    providers = [
        ProviderInformation(
            id="gemini",
            name="Google Gemini",
            enabled=gemini_enabled,
            active=LLM_PROVIDER == "gemini",
        ),
        ProviderInformation(
            id="openrouter",
            name="OpenRouter",
            enabled=openrouter_enabled,
            active=LLM_PROVIDER == "openrouter",
        ),
    ]

    return ProvidersResponse(
        active_provider=LLM_PROVIDER,
        providers=providers,
    )


@router.get(
    "/models",
    response_model=ModelsResponse,
)
def get_models() -> ModelsResponse:
    """
    Return the models configured for supported LLM providers.
    """
    active_model = get_active_model()

    models = [
        ModelInformation(
            id=GEMINI_MODEL,
            provider="gemini",
            enabled=bool(
                os.getenv("GEMINI_API_KEY")
            ),
            active=(
                LLM_PROVIDER == "gemini"
                and active_model == GEMINI_MODEL
            ),
        ),
        ModelInformation(
            id=OPENROUTER_MODEL,
            provider="openrouter",
            enabled=bool(
                os.getenv("OPENROUTER_API_KEY")
            ),
            active=(
                LLM_PROVIDER == "openrouter"
                and active_model == OPENROUTER_MODEL
            ),
        ),
    ]

    return ModelsResponse(
        active_model=active_model,
        models=models,
    )