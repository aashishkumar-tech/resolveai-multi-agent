"""Logging utilities for the ResolveAI backend."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "trace_id"):
            log_obj["trace_id"] = record.trace_id
        if hasattr(record, "duration_s"):
            log_obj["duration_s"] = record.duration_s
        if hasattr(record, "code"):
            log_obj["code"] = record.code
        if hasattr(record, "details"):
            log_obj["details"] = record.details

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, default=str)


class ConsoleFormatter(logging.Formatter):
    """Colored console formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console output."""
        color = self.COLORS.get(record.levelname, self.RESET)

        # Base format
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base = f"{timestamp} | {color}{record.levelname:8}{self.RESET} | {record.name} | {record.getMessage()}"

        # Add extra fields
        extras = []
        for key in ("trace_id", "duration_s", "code"):
            if hasattr(record, key):
                extras.append(f"{key}={getattr(record, key)}")

        if extras:
            base += f" | {' '.join(extras)}"

        return base


def _log_level() -> int:
    """Get log level from environment variable."""
    level = os.getenv("LOG_LEVEL", "INFO").upper().strip()
    return getattr(logging, level, logging.INFO)


def _use_json_logging() -> bool:
    """Determine if JSON logging should be used."""
    # Use JSON in production/cloud environments
    env = os.getenv("ENVIRONMENT", "development").lower()
    return env in ("production", "prod", "staging", "cloud")


def get_logger(name: str, *, level: int | None = None) -> logging.Logger:
    """
    Create or get a configured logger.

    Uses JSON formatting in production and colored console output in development.

    Args:
        name: Logger name (typically module path)
        level: Optional override for log level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers in hot reload
    if logger.handlers:
        return logger

    logger.setLevel(level or _log_level())

    handler = logging.StreamHandler(sys.stdout)

    if _use_json_logging():
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(ConsoleFormatter())

    logger.addHandler(handler)

    # Prevent double logging via root logger
    logger.propagate = False

    return logger


# Export for imports
__all__ = ["get_logger", "JSONFormatter", "ConsoleFormatter"]
