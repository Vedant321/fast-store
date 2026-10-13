# Stage 1: The builder

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_HTTP_TIMEOUT=120
WORKDIR /app


# Copy the dependency files first for docker caching
COPY pyproject.toml uv.lock ./


# Copy specific service files
COPY services/product-service/pyproject.toml services/product-service/

# Install dependencies for product-service
RUN uv sync --package product-service --frozen --no-dev

# Copy the rest of the code
COPY . .

# Stage 2: The Final Image
FROM python:3.12-slim-bookworm
WORKDIR /app

# Copy the env and the code from the builder
COPY --from=builder /app /app/
COPY --from=builder /app/services /app/services

# Put the virtual env on the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/services/product-service:/app"

# Run GRPC command

CMD ["python", "services/product-service/main.py"]

# Run the fast-api server
# CMD ["fastapi", "run", "services/product-service/main.py", "--port", "8000", "--host", "0.0.0.0"]
