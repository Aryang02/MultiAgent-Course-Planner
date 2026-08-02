# Deployment Guide

This guide covers deploying the MultiAgent Course Planner from local development through production.

## Deployment Options

| Environment | Approach | Notes |
|-------------|----------|-------|
| **Local dev** | `docker compose up` | Hot-reload with `API_SERVER=uvicorn` |
| **Staging** | Single-node Docker Compose or ECS task | Mirror production config at smaller scale |
| **Production** | Kubernetes or ECS | Separate deployments per service |

## Local Development

```bash
cp .env.example .env
# Set SECRET_KEY, GOOGLE_API_KEY, PINECONE_API_KEY

make up
```

For API hot-reload during development, add to `.env`:

```bash
API_SERVER=uvicorn
```

This starts uvicorn with `--reload` instead of Gunicorn.

### Verify deployment

```bash
curl http://localhost:8000/health    # {"status":"ok"}
curl http://localhost:8000/ready     # DB, Redis, Pinecone status
make test                            # 89 tests, 87% coverage
```

## Docker Compose (Staging / Single-Node)

The included `docker-compose.yml` runs all services on one host:

| Service | Replicas | Notes |
|---------|----------|-------|
| `api` | 1 | Gunicorn with `GUNICORN_WORKERS` (default: CPU count) |
| `worker` | 1 | 4 concurrent workers, all queues |
| `beat` | 1 | Scheduled maintenance tasks |
| `db` | 1 | PostgreSQL 17 with persistent volume |
| `redis` | 1 | Redis 7 with persistent volume |
| `mcp-*` | 1 each | 5 MCP tool servers |

### Build and start

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f api
```

### Run migrations manually

Migrations run automatically on API startup. To run manually:

```bash
docker compose exec api alembic upgrade head
```

## Production Deployment

### Recommended topology

Deploy each component as a separate service with independent scaling:

```
                    ┌─────────────┐
                    │  Load       │
                    │  Balancer   │
                    │  (TLS)      │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌────────┐  ┌────────┐  ┌────────┐
         │ API    │  │ API    │  │ API    │   (horizontal scale)
         │ :8000  │  │ :8000  │  │ :8000  │
         └────┬───┘  └────┬───┘  └────┬───┘
              │            │            │
              └────────────┼────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    ┌─────────┐      ┌──────────┐     ┌──────────┐
    │ Postgres│      │  Redis   │     │ Pinecone │
    │ 17      │      │  7       │     │ (cloud)  │
    └─────────┘      └────┬─────┘     └──────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         ┌────────┐ ┌────────┐  ┌────────┐
         │ Worker │ │ Worker │  │  Beat  │
         │(agents)│ │(ingest)│  │        │
         └────────┘ └────────┘  └────────┘
```

### API container

The API image uses Gunicorn + UvicornWorker by default:

```bash
gunicorn src.core.api:app -c gunicorn.conf.py
```

Key environment variables:

```bash
API_SERVER=gunicorn
GUNICORN_WORKERS=4          # 2 × CPU cores is a good starting point
GUNICORN_TIMEOUT=120        # Long uploads and agent polling
GUNICORN_BIND=0.0.0.0:8000
```

### Worker container

```bash
celery -A src.worker.celery_app worker \
  --loglevel=info \
  -Q ingestion,agents,notifications,maintenance,default \
  -c 4
```

For production, consider dedicated worker pools per queue:

```bash
# Agent pipeline workers (bottleneck)
celery -A src.worker.celery_app worker -Q agents -c 4 --hostname=agents@%h

# Ingestion workers
celery -A src.worker.celery_app worker -Q ingestion -c 2 --hostname=ingestion@%h
```

### Beat container

Run exactly one beat instance:

```bash
celery -A src.worker.celery_app beat --loglevel=info
```

### MCP servers

One instance of each MCP server is sufficient for most workloads. They are lightweight HTTP services:

| Container | Command | Port |
|-----------|---------|------|
| orchestrator | `python -m src.mcp.orchestrator_server` | 8001 |
| planner | `python -m src.mcp.planner_server` | 8002 |
| tutor | `python -m src.mcp.tutor_server` | 8003 |
| critic | `python -m src.mcp.critic_server` | 8004 |
| notes | `python -m src.mcp.notes_server` | 8005 |

Agents inside the worker container reach MCP servers via internal DNS (e.g. `http://mcp-tutor:8003/mcp/`).

## Environment Variables

### Required for production

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Long random string for JWT signing |
| `GOOGLE_API_KEY` | Gemini API key |
| `PINECONE_API_KEY` | Pinecone API key |
| `DB_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `CELERY_BROKER_URL` | Celery broker (usually same Redis) |
| `CELERY_RESULT_BACKEND` | Celery results (separate Redis DB recommended) |

### Recommended for production

| Variable | Value | Purpose |
|----------|-------|---------|
| `ENVIRONMENT` | `production` | Sentry tagging, log context |
| `LOG_JSON` | `true` | Machine-parseable logs |
| `LOG_LEVEL` | `INFO` | Avoid DEBUG in production |
| `SENTRY_DSN` | your DSN | Error tracking |
| `CORS_ORIGINS` | your frontend URL | Restrict cross-origin access |
| `APP_URL` | `https://your-domain.com` | Email links |

### Secrets management

Do not commit `.env` files or store secrets in Docker images. Use one of:

- **AWS:** Secrets Manager or SSM Parameter Store → inject as env vars in ECS/EKS task definitions
- **GCP:** Secret Manager → mount as env vars in Cloud Run / GKE
- **Kubernetes:** Sealed Secrets or external-secrets operator
- **HashiCorp Vault:** Dynamic secrets with sidecar injection

## Scaling Guidance

| Component | Strategy | When to scale |
|-----------|----------|---------------|
| **API** | Horizontal — add Gunicorn containers behind a load balancer | Response latency > 500ms at p95 |
| **Celery workers (agents)** | Horizontal — add workers on the `agents` queue | Queue depth > 10 sustained |
| **Celery workers (ingestion)** | Horizontal — add workers on the `ingestion` queue | Upload backlog growing |
| **MCP servers** | One instance each; scale if tool call volume grows | MCP latency > 1s |
| **PostgreSQL** | Vertical first; read replicas for chat history later | Connection pool exhaustion, slow queries |
| **Redis** | Single instance with AOF persistence; Redis Cluster if > 10k concurrent tasks | Memory pressure, connection limits |
| **Pinecone** | Serverless auto-scales; monitor query latency | p95 search latency > 200ms |

Monitor queue depth via the Prometheus metric `celery_queue_depth` exposed at `/metrics`.

## Production Checklist

### PostgreSQL

- [ ] Enable automated backups (daily minimum, point-in-time recovery preferred)
- [ ] Set `max_connections` appropriately (default 100; increase if running many API + worker replicas)
- [ ] Enable `pg_stat_statements` for slow query analysis
- [ ] Use a managed service (RDS, Cloud SQL, AlloyDB) in production
- [ ] Run Alembic migrations as a pre-deploy step, not only on API startup

### Redis

- [ ] Enable AOF persistence (`appendonly yes`)
- [ ] Set `maxmemory-policy allkeys-lru` to prevent OOM
- [ ] Use separate Redis databases: 0 = broker, 1 = results, 2+ = blocklist/cache
- [ ] Enable TLS for Redis connections in cloud environments

### Application

- [ ] Set a strong `SECRET_KEY` (64+ random bytes)
- [ ] Configure `CORS_ORIGINS` to your actual frontend domain
- [ ] Enable `SENTRY_DSN` for error tracking
- [ ] Set `ENVIRONMENT=production`
- [ ] TLS termination at the load balancer (not in the app container)
- [ ] Configure health check probes: liveness → `/health`, readiness → `/ready`

### Pinecone

- [ ] Use separate indexes per environment (dev, staging, prod)
- [ ] Monitor index size and query latency in the Pinecone dashboard
- [ ] Set appropriate dimension to match your embedding model

### Gemini API

- [ ] Set up quota alerts in Google Cloud Console
- [ ] Monitor `llm_tokens_total` Prometheus metric for cost tracking
- [ ] Implement retry/backoff for rate limit errors (Celery autoretry handles pipeline tasks)

### CI/CD

- [ ] GitHub Actions CI passes on every PR (lint, typecheck, test, build)
- [ ] Pre-commit hooks installed for local development
- [ ] Docker images tagged and pushed to a container registry
- [ ] Deploy only images that passed CI

## Health Checks

Configure your orchestrator with these probes:

| Probe | Endpoint | Expected | Interval |
|-------|----------|----------|----------|
| Liveness | `GET /health` | `200 {"status":"ok"}` | 10s |
| Readiness | `GET /ready` | `200 {"status":"ok",...}` | 15s |
| Startup | `GET /ready` | DB + Redis ok | 5s, 30s timeout |

Readiness returns `degraded` when Pinecone is unreachable but DB and Redis are ok. Decide whether to route traffic based on your RAG requirements.

## Graceful Shutdown

- **API (Gunicorn):** `GUNICORN_GRACEFUL_TIMEOUT=30` allows in-flight requests to complete
- **Celery workers:** `task_acks_late=True` ensures tasks are re-queued if a worker is killed mid-execution
- **Beat:** Only one beat instance; use leader election or a singleton deployment

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `/ready` shows `database: error` | Postgres not reachable | Check `DB_URL`, network, credentials |
| `/ready` shows `redis: error` | Redis not reachable | Check `REDIS_URL`, Redis container health |
| `/ready` shows `pinecone: error` | Invalid API key or network | Verify `PINECONE_API_KEY` |
| Tasks stuck in `pending` | No worker running | Check `docker compose ps worker`, worker logs |
| `401` on protected routes | Expired or revoked token | Re-login or call `/v1/refresh` |
| Upload returns 202 but document stays `pending` | Ingestion worker failure | Check worker logs, Pinecone/Gemini keys |
| Agent pipeline fails | Gemini quota or MCP unreachable | Check worker logs, MCP container health |

## Kubernetes Example (outline)

```yaml
# Simplified — adapt to your cluster
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-api
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: api
          image: your-registry/mcp-api:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: mcp-secrets
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 15
```

See [ARCHITECTURE.md](../ARCHITECTURE.md) for component details and [API.md](API.md) for endpoint reference.
