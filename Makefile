.PHONY: lint fmt check-env test

lint:
	uv run ruff check bot/ scripts/
	uv run ruff format --check bot/ scripts/

fmt:
	uv run ruff check --fix bot/ scripts/
	uv run ruff format bot/ scripts/

check-env:
	uv run python scripts/check_env.py

test:
	uv run pytest tests/ --cov=bot --cov=scripts --cov-report=term-missing
