# ResolveAI — Installation & Setup Guide (Local)

This guide explains how to set up and run the ResolveAI project on a new machine.

> Repo module: `hierarchical_app/`

---

## 1) Prerequisites

### Required software

- **Git** (to clone the repo)
- **Python 3.11+**
- **Node.js 18+**
- **Docker** (optional, for containerized deployment)
- (Windows) **PowerShell** / VS Code terminal

### Accounts / API keys

You must have:

- `GROQ_API_KEY`
- `TAVILY_API_KEY`

---

## 2) Folder structure (what matters)

After cloning, you should have:

```
<your-parent-folder>/
  hierarchical_app/
    backend/
    frontend/
    docs/
```

We will refer to:

- **Project root**: `<your-parent-folder>/hierarchical_app`
- **Backend root**: `<your-parent-folder>/hierarchical_app/backend`
- **Frontend root**: `<your-parent-folder>/hierarchical_app/frontend`

---

## 3) Backend setup (FastAPI)

### 3.1 Create a Python virtual environment

#### Windows (PowerShell)

From **Backend root**:

```
cd <your-parent-folder>\hierarchical_app\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Windows (CMD)

```
cd <your-parent-folder>\hierarchical_app\backend
python -m venv .venv
.\.venv\Scripts\activate.bat
```

> After activation, your prompt usually shows `(.venv)`.

### 3.2 Install Python dependencies

From **Backend root** (venv activated):

```
pip install -r requirements.txt
```

### 3.3 Configure backend environment variables

Copy the example env file and fill in your keys:

```
copy .env.example .env
```

Edit `.env` with your values:

```
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
LOG_LEVEL=INFO
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3.4 Run the backend

From **Backend root**:

```
python -m uvicorn app.main:app --reload --port 8000
```

Verify:

- Health: `http://127.0.0.1:8000/health`
- API Info: `http://127.0.0.1:8000/`
- Swagger Docs: `http://127.0.0.1:8000/docs`
- Chat endpoint: `POST http://127.0.0.1:8000/api/v1/chat`

### 3.5 Run tests

From **Backend root** (venv activated):

```
pytest tests/ -v
```

With coverage:

```
pytest tests/ -v --cov=app --cov-report=html
```

### 3.6 Run linting

```
ruff check app/
ruff format app/ --check
```

---

## 4) Frontend setup (Next.js)

### 4.1 Install Node dependencies

From **Frontend root**:

```
cd <your-parent-folder>\hierarchical_app\frontend
npm install
```

### 4.2 Configure frontend environment variables

Create a file:

- `<your-parent-folder>/hierarchical_app/frontend/.env.local`

Example (local backend):

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 4.3 Run the frontend

From **Frontend root**:

```
npm run dev
```

Open:

- `http://localhost:3000`

---

## 5) Common issues

### 5.1 Backend error: `ModuleNotFoundError: No module named 'app'`

You started uvicorn from the wrong folder.

Fix: run uvicorn from **Backend root**:

```
cd <your-parent-folder>\hierarchical_app\backend
python -m uvicorn app.main:app --reload --port 8000
```

### 5.2 Frontend error: invalid `favicon.ico`

If Next.js crashes due to `src/app/favicon.ico`, remove that file and clear `.next/` cache. The project uses icons from `public/`.

### 5.3 API errors / 500 on `/chat`

- Confirm `GROQ_API_KEY` and `TAVILY_API_KEY` exist in `backend/.env`
- Restart backend after changing `.env`

---

## 6) One-click local run (optional)

### Option A: VS Code tasks

Create VS Code tasks to start backend and frontend together.

### Option B: Docker Compose

From **Project root** (where `docker-compose.yml` is):

```
docker compose up --build
```

This starts both backend (port 8000) and frontend (port 3000).

To run in background:

```
docker compose up -d
```

To view logs:

```
docker compose logs -f
```

To stop:

```
docker compose down
```

---

## 7) CI/CD Pipeline

The project includes GitHub Actions workflows:

### CI Pipeline (`.github/workflows/ci.yml`)

Triggered on push to `main`/`develop` and pull requests:

1. **Backend Lint** — Ruff linter and formatter check
2. **Backend Tests** — Pytest with coverage
3. **Security Scan** — Bandit vulnerability scan
4. **Frontend Lint** — ESLint
5. **Frontend Build** — Next.js production build
6. **Docker Build** — Build both Docker images

### GCP Deploy (`.github/workflows/deploy-gcp.yml`)

Triggered on push to `main`:

1. Builds Docker images
2. Pushes to GCP Artifact Registry
3. Deploys to Cloud Run

### Setup Pre-commit Hooks

```
pip install pre-commit
pre-commit install
```

---

## 7) What to commit vs not commit

- ✅ commit code, docs, config templates (`.env.example`)
- ❌ do not commit secrets (`.env`, `.env.local`)
- ❌ do not commit `node_modules/` or `.next/`

(These are covered by the repo `.gitignore`.)
