"""Evaluation dataset loading utilities."""

import json
from pathlib import Path
from typing import Any


DATASET_PATH = Path(__file__).with_name(
    "dataset.json"
)


def load_dataset() -> list[dict[str, Any]]:
    """
    Load the local playlist evaluation dataset.

    Each dataset item is converted into the structure expected by
    Braintrust's Eval framework.
    """
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as dataset_file:
        raw_data = json.load(dataset_file)

    if not isinstance(raw_data, list):
        raise ValueError(
            "The evaluation dataset must contain a JSON list."
        )

    dataset: list[dict[str, Any]] = []

    for index, item in enumerate(raw_data):
        if not isinstance(item, dict):
            raise ValueError(
                "Every evaluation dataset item must be an object. "
                f"Invalid item found at index {index}."
            )

        dataset.append(
            {
                "input": item,
                "expected": None,
                "metadata": {
                    "dataset_index": index,
                    "requested_playlist_length": item.get(
                        "playlist_length"
                    ),
                },
            }
        )

    return dataset


def get_dataset_size() -> int:
    """
    Return the number of examples in the current evaluation dataset.
    """
    return len(
        load_dataset()
    )