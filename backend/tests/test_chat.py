"""Tests for the /api/v1/chat endpoint."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

CHAT_ENDPOINT = "/api/v1/chat"


class TestChatValidation:
    """Tests for request validation on the chat endpoint."""

    def test_missing_query_returns_422(self) -> None:
        """Request without query field should return 422."""
        response = client.post(CHAT_ENDPOINT, json={})
        assert response.status_code == 422

    def test_empty_query_returns_422(self) -> None:
        """Request with empty query string should return 422."""
        response = client.post(CHAT_ENDPOINT, json={"query": ""})
        assert response.status_code == 422

    def test_invalid_json_returns_422(self) -> None:
        """Request with invalid JSON should return 422."""
        response = client.post(
            CHAT_ENDPOINT,
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_wrong_field_type_returns_422(self) -> None:
        """Request with wrong field type should return 422."""
        response = client.post(CHAT_ENDPOINT, json={"query": 12345})
        assert response.status_code == 422


class TestChatSuccess:
    """Tests for successful chat responses."""

    @patch("app.api.v1.endpoints.run_workflow")
    def test_chat_returns_200(self, mock_runner) -> None:
        """Valid request should return 200 OK."""
        mock_runner.return_value = {
            "final_response": "Your order #12345 has been cancelled.",
            "trace_id": "test-trace-123",
            "duration_s": 2.5,
            "activity_log": [
                {"agent": "chief_manager", "action": "delegated"},
            ],
            "team_outputs": {
                "analysis": "Order cancellation request",
            },
        }

        response = client.post(
            CHAT_ENDPOINT,
            json={"query": "Cancel my order #12345"},
        )
        assert response.status_code == 200

    @patch("app.api.v1.endpoints.run_workflow")
    def test_chat_response_has_required_fields(self, mock_runner) -> None:
        """Response should contain all required fields."""
        mock_runner.return_value = {
            "final_response": "Your order has been cancelled successfully.",
            "trace_id": "test-trace-456",
            "duration_s": 1.8,
            "activity_log": [],
            "team_outputs": {},
        }

        response = client.post(
            CHAT_ENDPOINT,
            json={"query": "Cancel my order"},
        )
        data = response.json()

        assert "final_response" in data
        assert "trace_id" in data

    @patch("app.api.v1.endpoints.run_workflow")
    def test_chat_with_customer_support_query(self, mock_runner) -> None:
        """Test with a realistic customer support query."""
        mock_runner.return_value = {
            "final_response": "I understand your frustration. I've escalated your complaint and you'll receive a callback within 24 hours.",
            "trace_id": "test-trace-789",
            "duration_s": 4.1,
            "activity_log": [
                {"agent": "chief_manager", "action": "received_query", "detail": "Delegated to analysis"},
                {"agent": "analysis_manager", "action": "analyzed", "detail": "Sentiment: angry, Category: complaint"},
                {"agent": "research_manager", "action": "researched", "detail": "Found escalation policy"},
                {"agent": "quality_manager", "action": "reviewed", "detail": "Approved with empathy check"},
            ],
            "team_outputs": {
                "analysis": "Sentiment: angry, Category: service_complaint",
                "research": "Escalation policy: 24hr callback for complaints",
                "quality": "Response approved - empathetic tone verified",
            },
        }

        response = client.post(
            CHAT_ENDPOINT,
            json={"query": "Your service is terrible! I've been waiting 3 days for my delivery and nobody is helping me!"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data
        assert len(data["trace_id"]) > 0


class TestChatErrorHandling:
    """Tests for error handling in chat endpoint."""

    @patch("app.api.v1.endpoints.run_workflow")
    def test_workflow_exception_returns_500(self, mock_runner) -> None:
        """Workflow exception should return 500 error."""
        mock_runner.side_effect = Exception("LLM service unavailable")

        # TestClient re-raises exceptions by default, so use
        # raise_server_exceptions=False to let the global handler respond.
        with TestClient(app, raise_server_exceptions=False) as error_client:
            response = error_client.post(
                CHAT_ENDPOINT,
                json={"query": "Help me with my account"},
            )
        assert response.status_code == 500
