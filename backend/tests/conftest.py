"""Pytest configuration and fixtures for the test suite."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("TAVILY_API_KEY", "test-tavily-key")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("ENVIRONMENT", "development")


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    from app.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_chat_request() -> dict[str, str]:
    """Return a sample chat request payload."""
    return {
        "query": "I want to cancel my order #12345 and get a refund",
    }


@pytest.fixture
def sample_workflow_result() -> dict:
    """Return a sample workflow result."""
    return {
        "final_response": "I've processed your cancellation for order #12345. Your refund of $49.99 will be credited within 5-7 business days.",
        "trace_id": "test-trace-abc-123",
        "duration_s": 3.2,
        "activity_log": [
            {"agent": "chief_manager", "action": "received_query", "detail": "Delegated to analysis team"},
            {"agent": "analysis_manager", "action": "analyzed", "detail": "Classified as: order_cancellation"},
            {"agent": "research_manager", "action": "researched", "detail": "Found order details"},
            {"agent": "quality_manager", "action": "reviewed", "detail": "Response approved"},
        ],
        "team_outputs": {
            "analysis": "Sentiment: frustrated, Category: order_cancellation",
            "research": "Order #12345 found - Status: shipped, Amount: $49.99",
            "quality": "Response verified and approved",
        },
    }
