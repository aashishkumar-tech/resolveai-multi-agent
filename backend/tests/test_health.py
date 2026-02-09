"""Tests for health and root endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self) -> None:
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_body(self) -> None:
        """Health endpoint should return correct JSON body."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "resolveai"


class TestRootEndpoint:
    """Tests for the / root endpoint."""

    def test_root_returns_200(self) -> None:
        """Root endpoint should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_response_contains_api_info(self) -> None:
        """Root endpoint should return API information."""
        response = client.get("/")
        data = response.json()
        assert "service" in data
        assert "resolveai" in data["service"].lower() or "ResolveAI" in data["service"]
