# MultiAgent Course Planner

A multi-agent learning platform that generates personalized study plans from uploaded course materials using Google Gemini, MCP tool servers, and Pinecone vector search.

## Quick Start

```bash
cp .env.example .env
# Edit .env with your API keys

make install-dev
make up
```

API: http://localhost:8000/docs

## Development

```bash
make install-dev   # Install package + dev tools
make smoke         # Verify imports
make lint          # Ruff + mypy
make test          # Run pytest
make up            # Docker compose up
make down          # Docker compose down
```

## Stack

- Python 3.12, FastAPI, SQLAlchemy 2
- PostgreSQL 17, Redis 7, Celery 5.6
- Google Gemini, Pinecone, LangChain
- MCP + A2A agent protocols

See [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) for the full implementation plan.
