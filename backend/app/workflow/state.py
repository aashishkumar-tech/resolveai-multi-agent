from __future__ import annotations

from typing import Any

from langgraph.graph import MessagesState


class HierarchicalState(MessagesState):
    # Core query info
    customer_query: str
    customer_name: str
    mobile_number: str

    query_type: str
    urgency_level: str

    # Workflow control
    current_level: str
    next_agent: str
    active_department: str
    department_status: dict[str, str]

    # Analysis outputs
    query_classification: str
    research_data: str
    sentiment_analysis: str

    # Content outputs
    draft_response: str
    formatted_response: str

    # Quality outputs
    quality_review: str
    compliance_check: str
    final_response: str

    # Tracking
    iteration_count: int
    max_iterations: int
    activity_log: list[dict[str, Any]]
    department_reports: dict[str, dict[str, Any]]
    team_outputs: dict[str, str]
