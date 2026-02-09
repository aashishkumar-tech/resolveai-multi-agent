from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class RunArtifacts:
    trace_id: str
    query: str
    created_at: str
    final_response: str
    activity_log: list[dict[str, Any]]
    team_outputs: dict[str, Any]
    duration_s: float | None = None
    graph_png_path: str | None = None


def workspace_results_dir() -> Path:
    # Repo layout: AIAgent/hierarchical_app/backend/app/storage/persistence.py
    # We want:   AIAgent/Agents/hierarchical_results/
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "Agents" / "hierarchical_results"


def persist_run(artifacts: RunArtifacts) -> Path:
    out_dir = workspace_results_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    run_dir = out_dir / f"run_{ts}_{artifacts.trace_id[:8]}"
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "final.txt").write_text(artifacts.final_response, encoding="utf-8")
    (run_dir / "request.txt").write_text(artifacts.query, encoding="utf-8")

    payload = asdict(artifacts)
    (run_dir / "run.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return run_dir
