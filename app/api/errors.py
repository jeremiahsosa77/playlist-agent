"""Structured API exception handling."""

import logging

import requests
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: object | None = None,
) -> JSONResponse:
    """
    Create a consistent JSON error response.
    """
    error_data: dict[str, object] = {
        "code": code,
        "message": message,
    }

    if details is not None:
        error_data["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            {
                "error": error_data,
            }
        ),
    )


def register_exception_handlers(
    application: FastAPI,
) -> None:
    """
    Register shared exception handlers on the FastAPI application.
    """

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        return error_response(
            status_code=422,
            code="REQUEST_VALIDATION_ERROR",
            message="The request contained invalid data.",
            details=error.errors(),
        )

    @application.exception_handler(ValueError)
    async def handle_value_error(
        request: Request,
        error: ValueError,
    ) -> JSONResponse:
        return error_response(
            status_code=400,
            code="INVALID_PLAYLIST_DATA",
            message=str(error),
        )

    @application.exception_handler(requests.Timeout)
    async def handle_request_timeout(
        request: Request,
        error: requests.Timeout,
    ) -> JSONResponse:
        return error_response(
            status_code=504,
            code="EXTERNAL_SERVICE_TIMEOUT",
            message=(
                "An external service timed out while processing "
                "the playlist."
            ),
        )

    @application.exception_handler(requests.RequestException)
    async def handle_request_exception(
        request: Request,
        error: requests.RequestException,
    ) -> JSONResponse:
        logger.exception(
            "External service request failed."
        )

        return error_response(
            status_code=502,
            code="EXTERNAL_SERVICE_ERROR",
            message=(
                "An external service failed while processing "
                "the playlist."
            ),
        )

    @application.exception_handler(RuntimeError)
    async def handle_runtime_error(
        request: Request,
        error: RuntimeError,
    ) -> JSONResponse:
        logger.exception(
            "Playlist runtime error."
        )

        return error_response(
            status_code=502,
            code="PLAYLIST_PROCESSING_ERROR",
            message=str(error),
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unexpected API error."
        )

        return error_response(
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message=(
                "An unexpected error occurred while processing "
                "the request."
            ),
        )