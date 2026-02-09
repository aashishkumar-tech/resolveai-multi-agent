# ResolveAI - Hierarchical Multi-Agent Customer Service System

AI-powered customer service resolution system using a hierarchical multi-agent architecture built with LangGraph.

## Live Demo

- Frontend (Vercel): <https://resolveai-multi-agent-nu.vercel.app/>
- Backend (Cloud Run): <https://resolveai-backend-epgr7hjata-el.a.run.app>
- Backend health: <https://resolveai-backend-epgr7hjata-el.a.run.app/health>
- Backend API docs: <https://resolveai-backend-epgr7hjata-el.a.run.app/docs>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Chief Resolution Officer                │
│                    (Orchestrates all teams)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Analysis    │ │   Response    │ │   Quality     │
│   Manager     │ │   Manager     │ │   Manager     │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
   ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
   │ Workers │       │ Workers │       │ Workers │
   └─────────┘       └─────────┘       └─────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for containerized deployment)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment file and add your API keys
copy .env.example .env
# Edit .env with your GROQ_API_KEY and TAVILY_API_KEY

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access the Application

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>

## 📁 Project Structure

```
hierarchical_app/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Versioned API endpoints
│   │   ├── core/            # Config, logging, exceptions
│   │   ├── storage/         # Run persistence
│   │   └── workflow/        # LangGraph agents & tools
│   ├── tests/               # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # React components
│   │   └── lib/             # API client
│   ├── Dockerfile
│   └── package.json
├── docs/                    # Documentation
├── .github/workflows/       # CI/CD pipelines
├── docker-compose.yml
└── cloudbuild.yaml          # GCP Cloud Build config
```

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run linting
ruff check app/
ruff format app/ --check
```

## 🐳 Docker Deployment

### Local Docker Compose

```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Access Services

- Frontend: <http://localhost:3000>
- Backend: <http://localhost:8000>

## ☁️ GCP Cloud Run Deployment

### Prerequisites

1. [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Create a GCP project with billing enabled
3. Enable required APIs:

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Store Secrets

Important (Windows): avoid piping secrets via PowerShell because it can upload UTF-16 / non-UTF8 bytes.

Recommended approach:

1) Create UTF-8 text files (no BOM), e.g.:

- `C:\temp\groq.txt`
- `C:\temp\tavily.txt`

1) Upload as Secret Manager versions:

```bash
gcloud secrets create groq-api-key --data-file="C:\\temp\\groq.txt"
gcloud secrets create tavily-api-key --data-file="C:\\temp\\tavily.txt"
```

If the secrets already exist:

```bash
gcloud secrets versions add groq-api-key --data-file="C:\\temp\\groq.txt"
gcloud secrets versions add tavily-api-key --data-file="C:\\temp\\tavily.txt"
```

### Create Artifact Registry

```bash
gcloud artifacts repositories create resolveai \
    --repository-format=docker \
    --location=asia-south1 \
    --description="ResolveAI Docker images"
```

### Deploy via GitHub Actions

1. Create a service account with required permissions
2. Add `GCP_SA_KEY` and `GCP_PROJECT_ID` to GitHub Secrets
3. Push to `main` branch - deployment will trigger automatically

### Manual Deployment

```bash
# Build and deploy backend
cd backend
docker build -t asia-south1-docker.pkg.dev/PROJECT_ID/resolveai/backend:v1 .
docker push asia-south1-docker.pkg.dev/PROJECT_ID/resolveai/backend:v1

gcloud run deploy resolveai-backend \
    --image asia-south1-docker.pkg.dev/PROJECT_ID/resolveai/backend:v1 \
    --region asia-south1 \
    --platform managed \
    --allow-unauthenticated \
    --set-secrets GROQ_API_KEY=groq-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest
```

### Cloud Run persistence note

  Cloud Run containers can only write to `/tmp`. Run artifacts (run.json, graph.png, etc.) are stored under:

- `/tmp/resolveai/hierarchical_results`

  You can override the location with `RESOLVEAI_RESULTS_DIR`.

## ▲ Vercel Deployment (Frontend)

  1. Import the GitHub repo into Vercel.
  2. Set the **Root Directory** to `hierarchical_app/frontend`.
  3. Add environment variable:

     - `NEXT_PUBLIC_API_BASE_URL=https://resolveai-backend-epgr7hjata-el.a.run.app`

  4. Redeploy.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM | Required |
| `TAVILY_API_KEY` | Tavily API key for web search | Required |
| `ENVIRONMENT` | Environment (development/production) | development |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO |
| `LLM_MODEL` | LLM model to use | llama3-70b-8192 |
| `LLM_TEMPERATURE` | LLM temperature | 0.1 |
| `MAX_ITERATIONS` | Max workflow iterations | 10 |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | * |

## 📊 API Endpoints

### Health Check

```
GET /health
```

### Chat (v1)

```
POST /api/v1/chat
Content-Type: application/json

{
  "query": "What is my account balance?",
  "customer_name": "John Doe",
  "mobile_number": "1234567890"
}
```

### Get Run Details

```
GET /api/v1/runs/{trace_id}
```

### Stream Events

```
GET /api/v1/events?query=...
```

## 🔒 Security Features

- Rate limiting (10 requests/minute per IP)
- CORS configuration
- Non-root Docker containers
- Secret management via GCP Secret Manager
- Security scanning with Bandit

## 📈 Monitoring

- Structured JSON logging in production
- Trace ID for request tracking
- Health check endpoints for load balancers

## 🤝 Contributing

1. Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

1. Run tests before committing
2. Follow the existing code style (enforced by Ruff)

## 📄 License

MIT License - see LICENSE file for details.
