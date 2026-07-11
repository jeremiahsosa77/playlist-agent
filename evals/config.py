"""Central Braintrust evaluation configuration."""

import re
from dataclasses import dataclass
from typing import Any

from app.config import (
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    get_active_model,
)
from app.prompt import PROMPT_VERSION
from evals.metadata import (
    build_experiment_metadata,
)


def sanitize_experiment_value(
    value: str,
) -> str:
    """
    Convert a value into a Braintrust-friendly experiment-name segment.
    """
    sanitized_value = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        value.strip().lower(),
    )

    return sanitized_value.strip("-") or "unknown"


def format_temperature(
    temperature: float,
) -> str:
    """
    Format temperature consistently for experiment names.
    """
    return format(
        temperature,
        "g",
    )


@dataclass(frozen=True)
class EvaluationConfig:
    """
    Immutable configuration for one Braintrust evaluation experiment.
    """

    project_name: str
    experiment_name: str
    metadata: dict[str, Any]

    @classmethod
    def create(
        cls,
        dataset_size: int,
    ) -> "EvaluationConfig":
        """
        Build the evaluation configuration from active application settings.
        """
        provider = LLM_PROVIDER
        model = get_active_model()
        prompt_version = PROMPT_VERSION
        temperature = LLM_TEMPERATURE

        experiment_name = "--".join(
            [
                sanitize_experiment_value(
                    provider
                ),
                sanitize_experiment_value(
                    model
                ),
                sanitize_experiment_value(
                    prompt_version
                ),
                (
                    "temp-"
                    f"{sanitize_experiment_value(format_temperature(temperature))}"
                ),
                f"dataset-{dataset_size}",
            ]
        )

        return cls(
            project_name="Playlist Agent",
            experiment_name=experiment_name,
            metadata=build_experiment_metadata(
                dataset_size=dataset_size,
            ),
        )