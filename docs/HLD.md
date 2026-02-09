# ResolveAI — High Level Design (HLD)

## 1. Purpose

ResolveAI provides fast, consistent, and personalized customer support responses by orchestrating an **agentic / multi-agent style workflow** (multiple specialized steps and roles coordinated by LangGraph) behind a user-friendly web UI.

## 2. Goals

- Provide an end-user friendly chat experience.
- Orchestrate multi-step reasoning and retrieval (LangGraph).
- Persist run artifacts for audit/debug (optional but enabled).
- Offer transparency via an optional details view (graph + logs).

## 3. Non-goals

- Multi-tenant auth/user management.
- Payment, billing, or user provisioning.

## 4. System Context

### Components

- **Frontend** (Next.js): Collects customer details + query; renders answer.
- **Backend** (FastAPI): Receives chat requests; runs workflow; persists artifacts.
- **LLM** (Groq): Generates final response and intermediate reasoning steps.
- **Search Tool** (Tavily): Retrieves relevant web context.
- **Storage** (Filesystem): Stores run artifacts under `Agents/hierarchical_results/`.

## 5. Data Flow (Request → Response)

1. User enters customer name, mobile number, and query in UI.
2. Frontend calls `POST /chat`.
3. Backend constructs initial LangGraph state and runs workflow.
4. Workflow may call Tavily search and LLM nodes.
5. Backend post-processes output (personalization placeholder substitution).
6. Artifacts are stored (request, final answer, run.json, graph.png).
7. Backend returns final answer + trace id + duration.
8. Frontend shows answer (and optional details).

## 6. APIs

### Unversioned

- `GET /health` — Load balancer health check
- `GET /` — API information
- `GET /docs` — Swagger UI

### Versioned (v1)

- `POST /api/v1/chat` — Process customer query (rate limited)
- `GET /api/v1/runs/{trace_id}` — Retrieve run metadata
- `GET /api/v1/runs/{trace_id}/graph.png` — Workflow graph image
- `GET /api/v1/events?query=...` — SSE event stream

## 7. Observability

- **Structured logging**: JSON format in production, colored console in development
- **Trace IDs**: Every request gets a unique `trace_id` for end-to-end tracking
- Run artifacts include:
  - `run.json` with timings (`duration_s`), ids, and metadata
  - optional graph image
- Health check endpoint for monitoring and load balancers

## 8. Security considerations

- Secrets provided via env vars only (GCP Secret Manager in production).
- **Rate limiting**: 10 requests/minute per IP via SlowAPI.
- **CORS**: Configurable allowed origins via `ALLOWED_ORIGINS` env var.
- Non-root Docker containers for production.
- Avoid collecting sensitive data (UI warns about OTPs/passwords).
- Consider PII and retention policy for persisted artifacts.
- Security scanning with Bandit (integrated in CI pipeline).

## 9. Production / Deployment

- **Containerized**: Docker images for backend (Python) and frontend (Next.js).
- **Orchestration**: Docker Compose for local; GCP Cloud Run for production.
- **CI/CD**: GitHub Actions pipeline with lint → test → build → deploy stages.
- **Secrets**: GCP Secret Manager for API keys.
- **Region**: `asia-south1` (Mumbai) for low latency.
- **Scaling**: Cloud Run auto-scales 0–10 instances based on traffic.
- CORS locked to frontend origin in production.
- Structured JSON logging for log aggregation.
