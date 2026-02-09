# ResolveAI — Low Level Design (LLD)

## Live Demo (Production)

- Frontend (Vercel): <https://resolveai-multi-agent-nu.vercel.app/>
- Backend (Cloud Run): <https://resolveai-backend-epgr7hjata-el.a.run.app>
- Backend API docs: <https://resolveai-backend-epgr7hjata-el.a.run.app/docs>

## Deployment

For step-by-step setup and deployment instructions (Local, Docker Compose, and Vercel frontend configuration), see: `docs/INSTALLATION.md`.

## 1. Backend

### 1.1 Tech

- FastAPI (with API versioning: `/api/v1/`)
- Pydantic v2
- LangGraph
- Tavily search
- Groq LLM via `langchain-groq`
- SlowAPI (rate limiting)
- Structured logging (JSON in production, colored console in dev)

### 1.2 Key modules

- `app/main.py`
  - App initialization, lifespan, rate limiter, CORS, exception handlers
- `app/api/v1/__init__.py`
  - API v1 router registration
- `app/api/v1/endpoints.py`
  - Versioned route handlers (`/chat`, `/runs`, `/events`)
- `app/schemas.py`
  - Request/Response Pydantic models
- `app/core/logger.py`
  - Structured logging with `JSONFormatter` (production) and `ConsoleFormatter` (dev)
- `app/core/config.py`
  - Environment-based configuration via pydantic-settings
- `app/core/exception.py`
  - App-level exception types (`AppError`, `ExternalServiceError`, `ValidationError`)
- `app/workflow/*`
  - **Multi-agent / agentic workflow**: graph state, agent prompts (nodes), tool wrappers, runner
- `app/storage/persistence.py`
  - Filesystem persistence for run artifacts

### 1.3 Models

- `ChatRequest`
  - `query: str`
  - `customer_name?: str`
  - `mobile_number?: str`
- `ChatResponse`
  - `final_response: str`
  - `trace_id?: str`
  - `duration_s?: number`

### 1.4 Persistence format

Artifacts written under:

- Default: `/tmp/resolveai/hierarchical_results/run_<YYYYMMDD_HHMMSS>_<trace_id[:8]>/`
- Override via `RESOLVEAI_RESULTS_DIR` (or `RESULTS_DIR`)

Contains:

- `request.txt`
- `final.txt`
- `run.json` (metadata + duration_s)
- `graph.png` (if generated)

## 2. Frontend

### 2.1 Tech

- Next.js App Router (React)
- TailwindCSS

### 2.2 Key files

- `src/app/page.tsx`
  - Main UI & state
- `src/lib/api.ts`
  - API client
- `src/components/*`
  - UI primitives

### 2.3 UI behavior

- Tabs: Chat / Latest answer / Details
- Latest answer is collapsible
- Details panel lazy-loads trace when opened

## 3. Error handling

- Backend returns structured error responses:
  - `400` for validation errors
  - `429` for rate limit exceeded
  - `500` for internal errors
  - `502` for external service failures (LLM/search)
- All errors follow consistent JSON shape: `{"error": {"code", "message", "details"}}`
- Frontend provides loading states and disables send while running

## 4. Testing

- `tests/conftest.py` — Shared fixtures and test configuration
- `tests/test_health.py` — Health and root endpoint tests
- `tests/test_chat.py` — Chat endpoint tests (with mocked workflow)
- `tests/test_runner.py` — Workflow runner unit tests
- Run: `pytest tests/ -v --cov=app`

## 5. Code Quality

- **Linting**: Ruff (pycodestyle, pyflakes, isort, bugbear, etc.)
- **Type checking**: MyPy with strict mode
- **Security**: Bandit for vulnerability scanning
- **Pre-commit hooks**: Auto-format and lint on every commit

## 6. DevOps

- `Dockerfile` (backend) — Python 3.11-slim, non-root user, health check
- `Dockerfile` (frontend) — Multi-stage build with standalone Next.js output
- `docker-compose.yml` — Local orchestration of both services
- `.github/workflows/ci.yml` — CI pipeline (lint → test → build → docker)
- `.github/workflows/deploy-gcp.yml` — GCP Cloud Run deployment
- `cloudbuild.yaml` — GCP Cloud Build configuration
