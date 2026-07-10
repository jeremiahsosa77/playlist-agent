"""Shared Pydantic schema configuration."""

from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    """
    Convert a snake_case Python field name to camelCase for JSON.

    Example:
        playlist_length -> playlistLength
    """
    first_word, *remaining_words = value.split("_")

    return first_word + "".join(
        word.capitalize()
        for word in remaining_words
    )


class APIModel(BaseModel):
    """
    Base model for public API request and response schemas.

    Python code uses snake_case while serialized API data uses camelCase.
    Both naming styles are accepted when validating input.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )