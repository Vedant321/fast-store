# Stage 1: The builder

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app


# Copy the dependency files first for docker caching
COPY pyproject.toml uv.lock ./


# Copy specific service files
COPY services/user-service/pyproject.toml services/user-service/

# Install dependencies for user-service
RUN uv sync --package user-service --frozen --no-dev

# Copy the rest of the code
COPY . .

# Stage 2: The Final Image
FROM python:3.12-slim-bookworm
WORKDIR /app

# Copy the env and the code from the builder
COPY --from=builder /app /app/

ENV PYTHONPATH="/app/services/user-service:/app"

# Put the virtual env on the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/services/user-service:/app"

# Run the fast-api server
CMD ["fastapi", "run", "services/user-service/main.py", "--port", "8000", "--host", "0.0.0.0"]
