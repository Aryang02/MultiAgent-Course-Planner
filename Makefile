.PHONY: install install-dev lint format test migrate up down logs smoke frontend-install frontend-dev frontend-build codegen

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
	python3 scripts/smoke_imports.py

frontend-install:
	cd frontend && npm install

frontend-dev: frontend-install
	cd frontend && npm run dev

frontend-build: frontend-install
	cd frontend && npm run build

codegen: frontend-install
	cd frontend && npm run codegen
