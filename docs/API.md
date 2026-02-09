# ResolveAI — API Contract

Base URL (local): `http://localhost:8000`
Base URL (production): <https://resolveai-backend-epgr7hjata-el.a.run.app>

Swagger (production): <https://resolveai-backend-epgr7hjata-el.a.run.app/docs>
Health (production): <https://resolveai-backend-epgr7hjata-el.a.run.app/health>

Frontend (production): <https://resolveai-multi-agent-nu.vercel.app/>
API Version: `v1`
All versioned endpoints use the prefix: `/api/v1`

---

## Unversioned Endpoints

### GET /health

Health check endpoint for load balancers and monitoring.

#### Response (200) — /health

```json
{"status": "ok", "service": "resolveai"}
```

### GET /

Root endpoint with API information.

#### Response (200) — /

```json
{
  "service": "ResolveAI API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### GET /docs

Interactive Swagger UI documentation.

### GET /redoc

ReDoc API documentation.

---

## Versioned Endpoints (v1)

### POST /api/v1/chat

Process a customer query through the hierarchical agent workflow.

**Rate Limit**: 10 requests/minute per IP

#### Request

```json
{
  "query": "My payment failed but money was deducted",
  "customer_name": "Priya Sharma",
  "mobile_number": "+91XXXXXXXXXX"
}
```

Note: for compatibility, the backend also accepts `message` as an alias of `query`.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `query` | string | ✅ Yes | Customer query (min 1 char) |
| `customer_name` | string | No | Used for personalization |
| `mobile_number` | string | No | Used for personalization (min 5 chars) |

#### Response (200)

```json
{
  "final_response": "...",
  "trace_id": "uuid-string",
  "duration_s": 3.42,
  "customer_name": "Priya Sharma",
  "mobile_number": "+91XXXXXXXXXX"
}
```

#### Error (422 — Validation)

```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

#### Error (429 — Rate Limited)

```json
{
  "error": "Rate limit exceeded: 10 per 1 minute"
}
```

### GET /api/v1/runs/{trace_id}

Retrieve stored run metadata by trace ID.

#### Response (200) — /api/v1/runs/{trace_id}

```json
{
  "trace_id": "...",
  "query": "...",
  "final_response": "...",
  "duration_s": 2.5,
  "activity_log": [...],
  "graph_png_url": "/api/v1/runs/{trace_id}/graph.png"
}
```

### GET /api/v1/runs/{trace_id}/graph.png

Returns the workflow graph visualization image (PNG) if available.

### GET /api/v1/events?query=

Stream workflow events via Server-Sent Events (SSE).

---

## Error Response Format

All application errors follow this structure:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable message",
    "details": {}
  }
}
```

| HTTP Status | Code | Description |
| ----------- | ---- | ----------- |
| 400 | `validation_error` | Invalid request data |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `internal_server_error` | Unexpected server error |
| 502 | `external_service_error` | LLM/search service failure |
