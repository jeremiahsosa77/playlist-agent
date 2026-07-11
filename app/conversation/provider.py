"""LLM provider integration for adaptive playlist interviews."""

import os
import time
from collections.abc import Callable
from typing import Protocol

import requests
from google import genai
from google.genai import types

from app.config import (
    GEMINI_MODEL,
    LLM_PROVIDER,
    OPENROUTER_MODEL,
)
from app.conversation.config import (
    INTERVIEW_MAX_ATTEMPTS,
    INTERVIEW_MAX_QUESTIONS,
    INTERVIEW_REQUEST_TIMEOUT,
    INTERVIEW_RETRY_BASE_SECONDS,
    INTERVIEW_TEMPERATURE,
)
from app.conversation.models import (
    ConversationSession,
    InterviewAction,
)
from app.conversation.parser import (
    InterviewResponseParseError,
    parse_interview_action,
)
from app.conversation.prompt import (
    build_interview_prompt,
)


InterviewTextGenerator = Callable[[str], str]


class InterviewDecisionProvider(Protocol):
    """
    Interface for services that choose the next interview action.
    """

    def decide(
        self,
        session: ConversationSession,
    ) -> InterviewAction:
        """
        Return the next structured interview action.
        """


class InterviewProviderError(RuntimeError):
    """
    Raised when an interview provider cannot produce a valid action.
    """


class GeneratedTextInterviewProvider:
    """
    Interview provider backed by an injectable text-generation function.

    This is useful for unit tests and future provider implementations.
    """

    def __init__(
        self,
        text_generator: InterviewTextGenerator,
        max_questions: int = INTERVIEW_MAX_QUESTIONS,
    ) -> None:
        self._text_generator = text_generator
        self._max_questions = max_questions

    def decide(
        self,
        session: ConversationSession,
    ) -> InterviewAction:
        """
        Generate and parse the next interview action.
        """
        prompt = build_interview_prompt(
            session,
            max_questions=self._max_questions,
        )

        try:
            response_text = self._text_generator(
                prompt
            )

            return parse_interview_action(
                response_text
            )
        except InterviewResponseParseError as error:
            raise InterviewProviderError(
                "The interview provider returned an invalid response."
            ) from error


class ConfiguredInterviewProvider:
    """
    Interview provider using the application's active LLM configuration.
    """

    def __init__(
        self,
        provider: str = LLM_PROVIDER,
        max_questions: int = INTERVIEW_MAX_QUESTIONS,
    ) -> None:
        self._provider = provider.strip().lower()
        self._max_questions = max_questions

    def decide(
        self,
        session: ConversationSession,
    ) -> InterviewAction:
        """
        Ask the configured LLM provider for the next interview action.
        """
        prompt = build_interview_prompt(
            session,
            max_questions=self._max_questions,
        )

        last_error: Exception | None = None

        for attempt in range(
            1,
            INTERVIEW_MAX_ATTEMPTS + 1,
        ):
            try:
                print(
                    "Requesting interview decision using "
                    f"{self._provider} "
                    f"(attempt {attempt}/"
                    f"{INTERVIEW_MAX_ATTEMPTS})..."
                )

                response_text = self._generate_text(
                    prompt
                )

                return parse_interview_action(
                    response_text
                )

            except (
                InterviewResponseParseError,
                InterviewProviderError,
                requests.RequestException,
            ) as error:
                last_error = error

                if attempt >= INTERVIEW_MAX_ATTEMPTS:
                    break

                delay_seconds = (
                    INTERVIEW_RETRY_BASE_SECONDS
                    * (2 ** (attempt - 1))
                )

                time.sleep(
                    delay_seconds
                )

        raise InterviewProviderError(
            "The interview provider could not produce "
            "a valid decision."
        ) from last_error

    def _generate_text(
        self,
        prompt: str,
    ) -> str:
        """
        Generate raw response text using the active provider.
        """
        if self._provider == "openrouter":
            return self._generate_with_openrouter(
                prompt
            )

        if self._provider == "gemini":
            return self._generate_with_gemini(
                prompt
            )

        raise InterviewProviderError(
            "Unsupported interview LLM provider: "
            f"{self._provider}"
        )

    @staticmethod
    def _generate_with_openrouter(
        prompt: str,
    ) -> str:
        """
        Generate an interview decision through OpenRouter.
        """
        api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        if not api_key:
            raise InterviewProviderError(
                "OPENROUTER_API_KEY is missing "
                "from the environment."
            )

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": (
                    f"Bearer {api_key}"
                ),
                "Content-Type": "application/json",
                "X-OpenRouter-Title": (
                    "Playlist Agent Interview"
                ),
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": (
                    INTERVIEW_TEMPERATURE
                ),
            },
            timeout=INTERVIEW_REQUEST_TIMEOUT,
        )

        if not response.ok:
            raise InterviewProviderError(
                "OpenRouter returned an interview error: "
                f"{response.status_code} "
                f"{response.text}"
            )

        response_data = response.json()
        choices = response_data.get(
            "choices",
            [],
        )

        if not choices:
            raise InterviewProviderError(
                "OpenRouter returned no interview choices."
            )

        try:
            return choices[0][
                "message"
            ]["content"]
        except (
            KeyError,
            IndexError,
            TypeError,
        ) as error:
            raise InterviewProviderError(
                "OpenRouter returned an invalid "
                "interview response structure."
            ) from error

    @staticmethod
    def _generate_with_gemini(
        prompt: str,
    ) -> str:
        """
        Generate an interview decision through Gemini.
        """
        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise InterviewProviderError(
                "GEMINI_API_KEY is missing "
                "from the environment."
            )

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=INTERVIEW_TEMPERATURE,
                response_mime_type=(
                    "application/json"
                ),
            ),
        )

        if not response.text:
            raise InterviewProviderError(
                "Gemini returned an empty interview response."
            )

        return response.text