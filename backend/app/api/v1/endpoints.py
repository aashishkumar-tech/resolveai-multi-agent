"""API v1 endpoints for ResolveAI."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, StreamingResponse

from app.core.logger import get_logger
from app.schemas import ChatRequest, ChatResponse
from app.storage.persistence import RunArtifacts, persist_run, workspace_results_dir
from app.workflow.graph import build_graph
from app.workflow.runner import run_workflow, stream_workflow_events
from app.workflow.visualize import render_graph_png

router = APIRouter()
logger = get_logger("resolveai.api.v1")

# Build graph once at module load
GRAPH = build_graph()


def _personalize(text: str, customer_name: str | None, mobile_number: str | None) -> str:
    """Replace placeholder tokens with actual customer information."""
    out = text
    if customer_name:
        out = out.replace("[Customer name]", customer_name)
        out = out.replace("[Customer Name]", customer_name)
        out = out.replace("{Customer name}", customer_name)
        out = out.replace("{Customer Name}", customer_name)
    if mobile_number:
        out = out.replace("[Mobile number]", mobile_number)
        out = out.replace("[Mobile Number]", mobile_number)
        out = out.replace("{Mobile number}", mobile_number)
        out = out.replace("{Mobile Number}", mobile_number)
    return out


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request) -> ChatResponse:  # noqa: ARG001
    """
    Process a customer query through the hierarchical agent workflow.

    Returns the AI-generated response along with trace information.
    """
    trace_id = str(uuid.uuid4())

    logger.info(
        "Processing chat request",
        extra={"trace_id": trace_id, "query_length": len(req.query)},
    )

    result = run_workflow(
        GRAPH,
        req.query,
        trace_id=trace_id,
        customer_name=req.customer_name,
        mobile_number=req.mobile_number,
    )

    final_text = _personalize(
        result["final_response"],
        req.customer_name,
        req.mobile_number,
    )

    # Persist artifacts + render graph
    run_dir = persist_run(
        RunArtifacts(
            trace_id=trace_id,
            query=req.query,
            created_at=datetime.now(UTC).isoformat(),
            final_response=final_text,
            activity_log=result.get("activity_log", []),
            team_outputs=result.get("team_outputs", {}),
            duration_s=result.get("duration_s"),
        )
    )

    graph_path = run_dir / "graph.png"
    render_graph_png(GRAPH, graph_path)

    logger.info(
        "Chat request completed",
        extra={"trace_id": trace_id, "duration_s": result.get("duration_s")},
    )

    return ChatResponse(
        final_response=final_text,
        trace_id=trace_id,
        duration_s=result.get("duration_s"),
        customer_name=req.customer_name,
        mobile_number=req.mobile_number,
    )


@router.get("/runs/{trace_id}", response_model=None)
def get_run(trace_id: str):
    """Retrieve a stored run by trace ID."""
    base = workspace_results_dir()
    if not base.exists():
        return {"error": "no runs"}

    candidates = sorted(base.glob(f"run_*_{trace_id[:8]}"), reverse=True)
    if not candidates:
        return {"error": "not found"}

    run_dir = candidates[0]
    payload = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    payload["saved_dir"] = str(run_dir)
    payload["graph_png_url"] = f"/api/v1/runs/{trace_id}/graph.png"
    return payload


@router.get("/runs/{trace_id}/graph.png", response_model=None)
def get_run_graph(trace_id: str):
    """Retrieve the graph visualization for a run."""
    base = workspace_results_dir()
    candidates = sorted(base.glob(f"run_*_{trace_id[:8]}"), reverse=True)
    if not candidates:
        return {"error": "not found"}

    graph_path = candidates[0] / "graph.png"
    if not graph_path.exists():
        return {"error": "missing graph"}

    return FileResponse(str(graph_path), media_type="image/png")


@router.get("/events")
def events(query: str) -> StreamingResponse:
    """Stream workflow events for a query using Server-Sent Events."""
    trace_id = str(uuid.uuid4())

    async def gen() -> AsyncGenerator[bytes, None]:
        async for evt in stream_workflow_events(GRAPH, query, trace_id=trace_id):
            yield ("data: " + json.dumps(evt) + "\n\n").encode("utf-8")

    return StreamingResponse(gen(), media_type="text/event-stream")
