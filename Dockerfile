FROM python:3.12-slim

WORKDIR /app

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies (uses uv.lock if present)
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev

COPY bot/ ./bot/

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "bot.main"]
