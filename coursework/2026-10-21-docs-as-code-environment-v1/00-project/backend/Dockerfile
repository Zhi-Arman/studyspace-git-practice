FROM python:3.13-slim

# A fixed uv version keeps dependency installation reproducible with uv.lock.
COPY --from=ghcr.io/astral-sh/uv:0.11.17 /uv /uvx /usr/local/bin/
WORKDIR /app/backend
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
RUN mkdir -p /app/backend/data && useradd --create-home studyspace && chown -R studyspace:studyspace /app
USER studyspace
EXPOSE 8000
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
