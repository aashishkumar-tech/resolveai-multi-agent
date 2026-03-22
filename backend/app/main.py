"""Main FastAPI application for ResolveAI backend."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import router as v1_router
from app.core.exception import AppError
from app.core.logger import get_logger
from app.core.langsmith_setup import setup_langsmith

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

logger = get_logger("resolveai")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Application lifespan handler for startup/shutdown events."""
    logger.info("ResolveAI backend starting up...")
    # LangSmith tracing setup (no-op if API key missing)
    try:
        setup_langsmith()
    except Exception:
        logger.exception("Failed to initialize LangSmith tracing")
    yield
    logger.info("ResolveAI backend shutting down...")


app = FastAPI(
    title="ResolveAI - Hierarchical Agent API",
    description="AI-powered customer service resolution system using hierarchical multi-agent architecture.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(v1_router)


# Health check endpoint (unversioned for load balancer compatibility)
@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "ok", "service": "resolveai"}


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "service": "ResolveAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Exception handlers
@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Handle application-specific errors."""
    logger.warning(
        "AppError: %s",
        exc,
        extra={"code": exc.code, "details": exc.details},
    )
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details or {},
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.exception("Unhandled exception: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "Internal server error",
            }
        },
    )
