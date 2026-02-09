# ResolveAI — Technical Design Document (TDD)

## Live Demo (Production)

- Frontend (Vercel): <https://resolveai-multi-agent-nu.vercel.app/>
- Backend (Cloud Run): <https://resolveai-backend-epgr7hjata-el.a.run.app>
- Backend API docs: <https://resolveai-backend-epgr7hjata-el.a.run.app/docs>

## Deployment

For step-by-step setup and deployment instructions (Local, Docker Compose, and Vercel frontend configuration), see: `docs/INSTALLATION.md`.

## 1. Document control

- **System**: ResolveAI
- **Scope**: `hierarchical_app/` (FastAPI backend + Next.js frontend)
- **Status**: Living document

## 2. Executive summary

ResolveAI is a customer-support assistant that turns a user query plus customer details into a structured, actionable support response.

It is implemented as an **agentic / multi-agent style architecture**: multiple specialized steps (agents/roles) are orchestrated as nodes in a LangGraph workflow, with tool use (search) and generation (LLM) coordinated by the graph.

It uses:

- **LangGraph** to coordinate multi-step reasoning
- **Groq LLM** for generation
- **Tavily Search** for web/retrieved context
- **FastAPI** for an API layer
- **Next.js** for an end-user UI

## 3. Goals & non-goals

### 3.1 Goals

- Provide fast answers with consistent structure.
- Accept customer context (`customer_name`, `mobile_number`) for personalization.
- Persist artifacts per run for auditability and debugging.
- Provide optional transparency (workflow trace + graph).

### 3.2 Non-goals

- Authentication/authorization, user accounts.
- Multi-tenant separation.
- SLA-grade observability/metrics (can be added later).

## 4. Architecture overview

### 4.1 Components

- **Frontend (Next.js)**
  - Collects inputs
  - Calls backend
  - Shows answer + duration
  - Optional details tab for trace

- **Backend (FastAPI)**
  - Validates request
  - Runs LangGraph workflow
  - Persists artifacts
  - Returns response + `trace_id` + `duration_s`

- **External services**
  - Groq (LLM)
  - Tavily (Search)

### 4.2 Module boundaries (Backend)

- `app/main.py`: App initialization, lifespan, rate limiter, CORS, exception handlers
- `app/api/v1/`: Versioned API router and endpoints
- `app/schemas.py`: Pydantic request/response models
- `app/core/config.py`: env-based configuration via pydantic-settings
- `app/core/logger.py`: Structured logging (`JSONFormatter` for production, `ConsoleFormatter` for dev)
- `app/core/exception.py`: app-level exception types
- `app/storage/persistence.py`: artifact persistence to the filesystem
- `app/workflow/*`: LangGraph graph, nodes/agents, tools, runner

### 4.3 Module boundaries (Frontend)

- `src/app/page.tsx`: main UI composition and state
- `src/lib/api.ts`: HTTP client wrapper
- `src/components/*`: UI primitives and panels

## 5. Runtime flow

### 5.1 Request lifecycle

1. UI captures:
   - `customer_name`
   - `mobile_number`
   - `query`
2. UI sends `POST /api/v1/chat` to backend
3. Backend:
   - builds initial workflow state
   - executes LangGraph
   - computes `duration_s`
   - persists artifacts
4. Backend returns:
   - `final_response`
   - `trace_id`
   - `duration_s`
5. UI renders:
   - structured answer block
   - time taken

### 5.2 Details view lifecycle

1. User opens Details tab
2. UI requests `GET /api/v1/runs/{trace_id}`
3. UI displays:
   - metadata
   - optional graph image (via `graph_png_url`)

## 6. Data contracts

### 6.1 API: POST /api/v1/chat

#### Request

```json
{
  "query": "string",
  "customer_name": "string (optional)",
  "mobile_number": "string (optional)"
}
```

#### Response

```json
{
  "final_response": "string",
  "trace_id": "string (optional)",
  "duration_s": 0.0,
  "customer_name": "string (optional)",
  "mobile_number": "string (optional)"
}
```

### 6.2 Persistence schema (run.json)

At minimum:

```json
{
  "trace_id": "...",
  "started_at": "...",
  "duration_s": 2.34,
  "request": {
    "query": "...",
    "customer_name": "...",
    "mobile_number": "..."
  }
}
```

(Exact keys may evolve; treat file as an internal contract.)

## 7. Configuration

### 7.1 Backend

Loaded from `hierarchical_app/backend/.env`:

- `GROQ_API_KEY` (required)
- `TAVILY_API_KEY` (required)

Optional:

- `LOG_LEVEL` (defaults to INFO)
- `ENVIRONMENT` (defaults to development; set to `production` for JSON logging)
- `ALLOWED_ORIGINS` (comma-separated CORS origins, defaults to `*`)
- `LLM_MODEL` (defaults to `llama3-70b-8192`)
- `LLM_TEMPERATURE` (defaults to `0.1`)
- `MAX_ITERATIONS` (defaults to `10`)

### 7.2 Frontend

Loaded from `hierarchical_app/frontend/.env.local`:

- `NEXT_PUBLIC_API_BASE_URL`

## 8. Error handling

### 8.1 Backend

- `AppError` returned in a consistent JSON shape:

```json
{
  "error": {
    "code": "...",
    "message": "...",
    "details": {}
  }
}
```

- Unhandled exceptions return:
  - HTTP 500 + `internal_server_error`

### 8.2 Frontend

- Disables send while loading
- Shows “Generating…” and skeleton placeholders

## 9. Security & compliance

- Do not commit env files.
- Avoid requesting sensitive information (UI warning maintained).
- Persisted artifacts may contain PII => define retention and access policies.

## 10. Performance considerations

- The workflow is LLM-latency bound.
- Consider caching or streaming responses if needed.
- Consider limiting Tavily calls per request to control cost.

## 11. Testing strategy

### 11.1 Backend

- **Health tests** (`test_health.py`): Health and root endpoint verification
- **Chat tests** (`test_chat.py`): Endpoint validation, mocked workflow, customer info handling
- **Runner tests** (`test_runner.py`): Initial state, fallback logic, workflow execution
- **Shared fixtures** (`conftest.py`): Test client, sample data
- Run: `pytest tests/ -v --cov=app`

### 11.2 Code Quality

- **Ruff**: Linting + formatting (`ruff check app/` and `ruff format app/`)
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning
- **Pre-commit hooks**: Automated on every commit

### 11.3 Frontend

- Manual UI testing (current)
- Optional: add Playwright later

## 12. Deployment

### 12.1 Local

- Backend: `uvicorn app.main:app --reload --port 8000`
- Frontend: `npm run dev`
- Docker: `docker compose up --build`

### 12.2 Production (GCP Cloud Run)

- **CI/CD**: GitHub Actions pipeline (`.github/workflows/`)
- **Container Registry**: GCP Artifact Registry (`asia-south1`)
- **Secrets**: GCP Secret Manager for API keys
- **Backend**: Cloud Run (1 CPU, 1GB RAM, 0–10 instances)
- **Frontend**: Cloud Run (1 CPU, 256MB RAM, 0–5 instances)
- **Region**: `asia-south1` (Mumbai)

### 12.3 Configuration Files

- `backend/Dockerfile` — Backend container image
- `frontend/Dockerfile` — Frontend container image (multi-stage)
- `docker-compose.yml` — Local multi-service orchestration
- `.github/workflows/ci.yml` — CI pipeline
- `.github/workflows/deploy-gcp.yml` — GCP deployment
- `cloudbuild.yaml` — GCP Cloud Build config
- `.pre-commit-config.yaml` — Pre-commit hooks

## 13. Appendix

### 13.1 Directory references

- See `HLD.md` / `LLD.md` / `API.md` for focused docs.
