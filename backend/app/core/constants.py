"""Constants shared across the backend.

Keep values here stable and avoid importing heavy modules to prevent import-time side-effects.
"""

from __future__ import annotations

APP_NAME = "ResolveAI"
API_PREFIX = ""  # reserved for future versioning like "/api/v1"

DEFAULT_LLM_MODEL = "llama-3.1-8b-instant"
DEFAULT_LLM_TEMPERATURE = 0.1
DEFAULT_MAX_ITERATIONS = 15

RUNS_DIR = "Agents/hierarchical_results"
