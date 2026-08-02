# API Reference

The MultiAgent Course Planner exposes a REST API at `/v1/*`. Interactive documentation is available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Authentication

Most endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Obtain tokens via `POST /v1/login`. Access tokens expire in 15 minutes; use `POST /v1/refresh` to rotate.

## Endpoints

### Health and metrics

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Liveness probe — returns `{"status":"ok"}` |
| `GET` | `/ready` | No | Readiness probe — checks DB, Redis, Pinecone |
| `GET` | `/metrics` | No | Prometheus metrics (latency, queue depth, LLM tokens) |

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/v1/register` | No | Create account |
| `POST` | `/v1/login` | No | Get access + refresh tokens |
| `POST` | `/v1/refresh` | No | Rotate token pair |
| `POST` | `/v1/logout` | Optional Bearer | Revoke session |
| `GET` | `/v1/me` | Yes | Current user profile |

#### Register

```http
POST /v1/register
Content-Type: application/json

{
  "username": "alice",
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

Response `201`:

```json
{
  "id": "uuid",
  "username": "alice",
  "email": "alice@example.com"
}
```

#### Login

```http
POST /v1/login
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

Response `200`:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "alice",
    "email": "alice@example.com"
  }
}
```

#### Refresh

```http
POST /v1/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

Returns a new token pair (same shape as login).

#### Logout

```http
POST /v1/logout
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

Response `204` (no body).

### Chats

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/v1/chats` | Yes | Create a new chat session |
| `GET` | `/v1/chats` | Yes | List all chats for the user |
| `GET` | `/v1/chats/{chat_id}` | Yes | Get chat messages |

#### Create chat

```http
POST /v1/chats
Authorization: Bearer <token>
```

Response `201`:

```json
{
  "chat_id": "uuid"
}
```

### Documents

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/v1/upload` | Yes | Upload files for ingestion |
| `GET` | `/v1/documents` | Yes | List uploaded documents |
| `GET` | `/v1/documents/{document_id}` | Yes | Get document status |

#### Upload

```http
POST /v1/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

documents: <file1>, <file2>
index_name: vector_db_index  (optional)
```

Response `202`:

```json
{
  "task_id": "celery-task-uuid",
  "detail": "Document ingestion started",
  "files_uploaded": 2,
  "document_ids": ["uuid1", "uuid2"],
  "status": "pending"
}
```

Supported formats: `.txt`, `.docx`. Max 50 MB per file, 200 MB per request.

Poll ingestion status via `GET /v1/tasks/{task_id}`.

### Study plan generation

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/v1/generate` | Yes | Request a study plan (async) |
| `GET` | `/v1/tasks/{task_id}` | Yes | Poll task status |

#### Generate

```http
POST /v1/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "Create a study plan for linear algebra",
  "chat_id": "uuid"
}
```

Response `202`:

```json
{
  "task_id": "celery-task-uuid",
  "status": "pending",
  "message": "Generation task accepted"
}
```

#### Poll task status

```http
GET /v1/tasks/{task_id}
Authorization: Bearer <token>
```

Response `200` (completed):

```json
{
  "task_id": "celery-task-uuid",
  "status": "completed",
  "result": {
    "study_topics": ["Vectors", "Matrices"],
    "notes": { "...": "..." },
    "test": { "questions": [] },
    "plan_id": "uuid",
    "run_id": "uuid",
    "status": "completed"
  }
}
```

Task status values: `pending`, `processing`, `completed`, `failed`.

### Study plans

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/v1/study-plans` | Yes | List all study plans |
| `GET` | `/v1/study-plans/{plan_id}` | Yes | Get a specific study plan |

## Typical workflow

```
1. POST /v1/register          → create account
2. POST /v1/login             → get tokens
3. POST /v1/chats             → create chat session
4. POST /v1/upload            → upload course materials
5. GET  /v1/tasks/{task_id}   → wait for ingestion to complete
6. POST /v1/generate          → request study plan
7. GET  /v1/tasks/{task_id}   → wait for pipeline to complete
8. GET  /v1/study-plans       → list generated plans
```

## Error responses

All errors return JSON:

```json
{
  "detail": "Human-readable error message",
  "request_id": "uuid"
}
```

| Status | Meaning |
|--------|---------|
| `400` | Bad request (validation, missing fields) |
| `401` | Unauthorized (missing/invalid/expired token) |
| `403` | Forbidden (e.g. accessing another user's task) |
| `404` | Resource not found |
| `409` | Conflict (e.g. duplicate email) |
| `422` | Validation error (Pydantic) |
| `429` | Rate limit exceeded |
| `500` | Internal server error |

## Rate limits

| Endpoint | Limit |
|----------|-------|
| `POST /v1/login` | 10 requests/minute per IP |
| `POST /v1/refresh` | 30 requests/minute per IP |
| `POST /v1/generate` | 20 requests/minute per IP |

## Request tracing

Every response includes an `X-Request-ID` header. Include your own via the request header for correlation:

```
X-Request-ID: my-trace-id-123
```

This ID appears in structured logs and error responses.
