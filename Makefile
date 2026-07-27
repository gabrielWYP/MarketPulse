.PHONY: install lint format-check typecheck test secret-scan compose-config check

install:
	uv sync --all-groups

lint:
	uv run ruff check .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy

test:
	uv run pytest

secret-scan:
	./scripts/scan-secrets.sh

compose-config:
	docker compose --env-file .env.example config --quiet

check: lint format-check typecheck test secret-scan compose-config
