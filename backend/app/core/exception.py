"""Centralized exception types for the ResolveAI backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AppError(Exception):
    """Base application exception.

    Args:
        message: End-user safe error message.
        code: Stable error code for clients/logging.
        details: Optional extra details (avoid secrets/PII).
        http_status: Suggested HTTP status code.
    """

    message: str
    code: str = "app_error"
    details: dict[str, Any] | None = None
    http_status: int = 500

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code}: {self.message}"


class ExternalServiceError(AppError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(
            message=message, code="external_service_error", details=details, http_status=502
        )


class ValidationError(AppError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message=message, code="validation_error", details=details, http_status=400)
