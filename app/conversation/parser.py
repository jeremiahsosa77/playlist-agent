"""Parsing and validation for interview model responses."""

import json

from pydantic import ValidationError

from app.conversation.models import (
    InterviewAction,
)
from app.conversation.state import (
    InterviewActionType,
)


class InterviewResponseParseError(ValueError):
    """
    Raised when an interview model response cannot be parsed safely.
    """


def remove_markdown_fences(
    text: str,
) -> str:
    """
    Remove common JSON Markdown fences from a model response.
    """
    cleaned_text = text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[
            len("```json"):
        ].strip()
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[
            len("```"):
        ].strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3].strip()

    return cleaned_text


def parse_interview_action(
    text: str,
) -> InterviewAction:
    """
    Parse and validate an LLM response as a structured interview action.

    Model-generated ready actions must include a playlist brief.
    """
    if not isinstance(text, str) or not text.strip():
        raise InterviewResponseParseError(
            "The interview model returned an empty response."
        )

    cleaned_text = remove_markdown_fences(
        text
    )

    try:
        raw_action = json.loads(
            cleaned_text
        )
    except json.JSONDecodeError as error:
        raise InterviewResponseParseError(
            "The interview model response was not valid JSON."
        ) from error

    if not isinstance(raw_action, dict):
        raise InterviewResponseParseError(
            "The interview model response must be a JSON object."
        )

    try:
        action = InterviewAction.model_validate(
            raw_action
        )
    except ValidationError as error:
        raise InterviewResponseParseError(
            "The interview model returned an invalid action."
        ) from error

    if (
        action.action
        == InterviewActionType.READY_TO_GENERATE
        and action.brief is None
    ):
        raise InterviewResponseParseError(
            "A ready-to-generate response must include "
            "a playlist brief."
        )

    return action