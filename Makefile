.PHONY: install install-dev lint format test migrate up down logs smoke

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

lint:
	ruff check src tests
	mypy src || true

format:
	ruff format src tests
	ruff check --fix src tests

test:
	python3 -m pytest

migrate:
	alembic upgrade head

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api

smoke:
	python scripts/smoke_imports.py
