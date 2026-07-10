"""LLM provider and model configuration schemas."""

from app.schemas.common import APIModel


class ProviderInformation(APIModel):
    """
    Information about one supported LLM provider.
    """

    id: str
    name: str
    enabled: bool
    active: bool


class ProvidersResponse(APIModel):
    """
    Supported LLM providers and the currently active provider.
    """

    active_provider: str
    providers: list[ProviderInformation]


class ModelInformation(APIModel):
    """
    Information about one configured LLM model.
    """

    id: str
    provider: str
    enabled: bool
    active: bool


class ModelsResponse(APIModel):
    """
    Configured models and the currently active model.
    """

    active_model: str
    models: list[ModelInformation]