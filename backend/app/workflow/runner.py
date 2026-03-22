from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import HumanMessage

from app.core.config import settings


def _initial_state(
    query: str, customer_name: str | None = None, mobile_number: str | None = None
) -> dict[str, Any]:
    return {
        "messages": [HumanMessage(content=query)],
        "customer_query": query,
        "customer_name": customer_name or "",
        "mobile_number": mobile_number or "",
        "query_type": "",
        "urgency_level": "",
        "current_level": "chief",
        "next_agent": "analysis_manager",
        "active_department": "",
        "department_status": {},
        "query_classification": "",
        "research_data": "",
        "sentiment_analysis": "",
        "draft_response": "",
        "formatted_response": "",
        "quality_review": "",
        "compliance_check": "",
        "final_response": "",
        "iteration_count": 0,
        "max_iterations": settings.max_iterations,
        "activity_log": [],
        "department_reports": {},
        "team_outputs": {},
    }


def run_workflow(
    graph,
    query: str,
    trace_id: str | None = None,
    customer_name: str | None = None,
    mobile_number: str | None = None,
) -> dict[str, Any]:
    start = time.time()
    state = _initial_state(query, customer_name=customer_name, mobile_number=mobile_number)
    result = graph.invoke(state)

    return {
        "final_response": result.get("final_response") or _fallback_final(result),
        "trace_id": trace_id,
        "duration_s": round(time.time() - start, 3),
        "activity_log": result.get("activity_log", []),
        "team_outputs": result.get("team_outputs", {}),
    }


async def stream_workflow_events(
    graph, query: str, trace_id: str | None = None
) -> AsyncGenerator[dict[str, Any], None]:
    # LangGraph streaming depends on version; use iterative invoke steps when available.
    # Here, we emit coarse-grained events for UI (start/end + final).
    yield {"type": "start", "trace_id": trace_id, "query": query}
    result = run_workflow(graph, query, trace_id=trace_id)
    yield {"type": "final", **result}


def _fallback_final(result: dict[str, Any]) -> str:
    # Prefer formatted_response if final_response wasn't set
    return (
        result.get("formatted_response") or result.get("draft_response") or "No response generated."
    )
