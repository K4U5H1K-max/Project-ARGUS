from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, message: str, *, details: Any | None = None, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str, *, details: Any | None = None) -> None:
        super().__init__("not_found", message, details=details, status_code=404)


class ValidationAppError(AppError):
    def __init__(self, message: str, *, details: Any | None = None) -> None:
        super().__init__("validation_error", message, details=details, status_code=422)


class KafkaPublishError(AppError):
    def __init__(self, message: str, *, details: Any | None = None) -> None:
        super().__init__("kafka_publish_error", message, details=details, status_code=502)


class ConcurrencyError(AppError):
    def __init__(self, message: str, *, details: Any | None = None) -> None:
        super().__init__("concurrency_error", message, details=details, status_code=409)


def error_response(code: str, message: str, *, details: Any | None = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_response(exc.code, exc.message, details=exc.details))

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=error_response("validation_error", "Request validation failed", details=exc.errors()))

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_response("http_error", str(exc.detail)))

    @app.exception_handler(Exception)
    async def handle_uncaught(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content=error_response("internal_server_error", "An unexpected error occurred"))
