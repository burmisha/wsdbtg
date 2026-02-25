.PHONY: lint fmt test

lint:
	uv run ruff check bot/
	uv run ruff format --check bot/

fmt:
	uv run ruff check --fix bot/
	uv run ruff format bot/

test:
	uv run pytest tests/ --cov=bot --cov-report=term-missing
