# MultiAgent Course Planner

A multi-agent learning platform that generates personalized study plans from uploaded course materials. Users upload documents, start a chat, and request a study plan — a coordinated agent pipeline (Planner → Tutor → Notes → Critic) runs asynchronously and persists the result.

## Features

- User registration, login, JWT refresh/logout
- Document upload (TXT, DOCX) with async Celery ingestion into Pinecone
- Multi-agent study plan generation with RAG over user documents
- Chat history and study plan management
- MCP tool servers for agent-to-database integration
- Prometheus metrics, structured JSON logging, optional Sentry

## Quick Start

**Prerequisites:** Docker, Docker Compose, and API keys for [Google Gemini](https://ai.google.dev/) and [Pinecone](https://www.pinecone.io/).

```bash
git clone https://github.com/Aryang02/MultiAgent-Course-Planner.git
cd MultiAgent-Course-Planner

cp .env.example .env
# Edit .env — at minimum set SECRET_KEY, GOOGLE_API_KEY, PINECONE_API_KEY

make up
```

Wait for all services to become healthy (~30 seconds), then open:

| URL | Purpose |
|-----|---------|
| http://localhost:8000/docs | Interactive API docs (Swagger) |
| http://localhost:8000/health | Liveness probe |
| http://localhost:8000/ready | Readiness probe (DB, Redis, Pinecone) |
| http://localhost:8000/metrics | Prometheus metrics |

### First API call

```bash
# Register
curl -s -X POST http://localhost:8000/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"password123"}'

# Login
curl -s -X POST http://localhost:8000/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"password123"}'

# Use the access_token from the response as Bearer token for protected routes
```

See [docs/API.md](docs/API.md) for the full endpoint reference.

## Architecture (summary)

```
Client → FastAPI (Gunicorn) → PostgreSQL 17
                ↓                    ↑
           Redis 7 ← Celery Worker → Agents pipeline
                ↓                    ↓
           Task results          Pinecone (per-user namespaces)
                                     ↓
                              MCP tool servers (8001–8005)
```

- **API** (`src/api/`) — FastAPI app with auth, upload, generate, chats, study plans
- **Worker** (`src/worker/`) — Celery tasks for ingestion, agent pipeline, email
- **Agents** (`src/agents/`) — Planner, Tutor, Notes, Critic coordinated via `AgentExecutor`
- **MCP servers** (`src/mcp/`) — Database and vector search tools for agents
- **RAG** (`src/database/`) — Document ingestion, chunking, Pinecone indexing

Full details: [ARCHITECTURE.md](ARCHITECTURE.md)

## Development

```bash
make install-dev   # pip install -e ".[dev]"
make smoke         # Verify all modules import
make test          # pytest with 80% coverage gate (89 tests)
make lint          # ruff + mypy
make format        # ruff format + auto-fix
make up            # docker compose up --build -d
make down          # docker compose down
make logs          # tail API logs
make migrate       # alembic upgrade head
```

For local API reload without Gunicorn, set `API_SERVER=uvicorn` in `.env`.

### Pre-commit hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | JWT signing key (use a long random string) |
| `GOOGLE_API_KEY` | Yes | — | Google Gemini API key |
| `PINECONE_API_KEY` | Yes | — | Pinecone API key |
| `DB_URL` | Yes | local postgres | SQLAlchemy connection string |
| `REDIS_URL` | Yes | `redis://redis:6379/0` | Redis for cache and blocklist |
| `CELERY_BROKER_URL` | Yes | `redis://redis:6379/0` | Celery message broker |
| `CELERY_RESULT_BACKEND` | Yes | `redis://redis:6379/1` | Celery result store |
| `CORS_ORIGINS` | No | `localhost:3000,8000` | Comma-separated allowed origins |
| `APP_URL` | No | `http://localhost` | Base URL for email links |
| `EMAIL_HOST` / `EMAIL_PORT` | No | Gmail defaults | SMTP for welcome emails |
| `MAX_UPLOAD_FILE_SIZE_MB` | No | `50` | Per-file upload limit |
| `LOG_LEVEL` | No | `INFO` | Log verbosity |
| `LOG_JSON` | No | `true` | JSON structured logs |
| `SENTRY_DSN` | No | — | Sentry error tracking |
| `API_SERVER` | No | `gunicorn` | `uvicorn` for dev reload |
| `GUNICORN_WORKERS` | No | CPU count | Gunicorn worker processes |
| `GUNICORN_TIMEOUT` | No | `120` | Request timeout (seconds) |

See [.env.example](.env.example) for the complete list.

## Docker Services

| Service | Port | Role |
|---------|------|------|
| `api` | 8000 | FastAPI application |
| `worker` | — | Celery worker (ingestion, agents, notifications) |
| `beat` | — | Celery beat scheduler |
| `db` | 5432 | PostgreSQL 17 |
| `redis` | 6379 | Redis 7 |
| `mcp-orchestrator` | 8001 | Chat history, plan lookup |
| `mcp-planner` | 8002 | Save study plans |
| `mcp-tutor` | 8003 | Document search (RAG) |
| `mcp-critic` | 8004 | Agent conversation logs |
| `mcp-notes` | 8005 | Agent conversation logs |

## Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| API | FastAPI, Gunicorn + Uvicorn workers |
| ORM / Migrations | SQLAlchemy 2, Alembic |
| Task queue | Celery 5.6, Redis 7 |
| Database | PostgreSQL 17 |
| Vector store | Pinecone (per-user namespaces) |
| LLM | Google Gemini |
| Agents | Custom executor + MCP + A2A discovery |
| Observability | structlog, Prometheus, Sentry (optional) |
| CI | GitHub Actions (lint, typecheck, test, build) |

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, data flow, component details |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment, scaling, checklist |
| [docs/API.md](docs/API.md) | REST API endpoint reference |
| [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) | Phased implementation history |

## License

See repository for license details.
