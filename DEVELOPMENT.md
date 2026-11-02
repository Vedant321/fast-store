# Fast Store Developer Guide

This guide is for working on the project locally: managing Python dependencies, rebuilding services, inspecting infrastructure, and running the current Kubernetes exercise.

## Tooling and project layout

The repository is a `uv` workspace using Python 3.12.

```text
fast-store/
├── services/
│   ├── user-service/       # REST API, PostgreSQL, JWT, gRPC client
│   ├── product-service/    # gRPC server
│   ├── order-service/      # REST event publisher
│   └── inventory-service/  # RabbitMQ event consumer and DLQ example
├── k8s/                    # Current introductory Kubernetes manifests
├── compose.yaml            # Local Docker Compose stack
├── promtail-config.yaml    # Docker log discovery and Loki destination
├── pyproject.toml          # Root uv workspace definition
└── uv.lock                 # Reproducible dependency lock file
```

## Local Python environment

Install all workspace dependencies:

```bash
uv sync
```

Activate the created virtual environment only when you want to run Python tools directly:

```bash
source .venv/bin/activate
python --version
```

You do not install Docker, Kubernetes, `kubectl`, or Minikube with `uv`. They are host-level development tools, independent of the Python virtual environment.

## Dependency management

Add a dependency to one microservice with `--package`:

```bash
uv add <package-name> --package user-service
```

Examples of valid workspace package names are:

```text
user-service
product-service
order-service
inventory-service
```

After editing a `pyproject.toml` manually, refresh the lock file:

```bash
uv lock
uv sync
```

Commit both the changed `pyproject.toml` and `uv.lock`. Docker builds use `uv sync --frozen`, so an out-of-date lock file will make a container build fail.

## Docker Compose workflow

Validate the Compose file without starting containers:

```bash
docker compose config --quiet
```

Build and run the full local stack:

```bash
docker compose up --build
```

Useful day-to-day commands:

```bash
# Start in the background
docker compose up --build -d

# Rebuild and restart one service after changing its code or Dockerfile
docker compose up --build -d user-service

# Follow one service's logs
docker compose logs -f user-service

# See service and container status
docker compose ps

# Stop containers; PostgreSQL data remains in its named volume
docker compose down
```

Do not delete the PostgreSQL volume unless you intentionally want to remove local database data.

## Services and ports

| Component | Host port | Container port | Purpose |
| --- | ---: | ---: | --- |
| Traefik | 80 | 80 | User-service public gateway |
| Traefik dashboard | 8080 | 8080 | Development routing dashboard |
| Order service | 8002 | 8000 | REST order API |
| Inventory service | 8003 | 8000 | REST mock-inventory API |
| PostgreSQL | 5433 | 5432 | Local database access |
| RabbitMQ AMQP | 5672 | 5672 | Application messaging |
| RabbitMQ Management | 15672 | 15672 | Queue and message inspection |
| Jaeger | 16686 | 16686 | Trace viewer |
| Jaeger OTLP gRPC | 4317 | 4317 | Telemetry receiver |
| Loki | 3100 | 3100 | Log-store API |
| Grafana | 3000 | 3000 | Logs dashboard and Explore |

Product service intentionally has no host port: it is an internal gRPC service reached by other Compose services.

## RabbitMQ and dead-letter queue

The Order service publishes messages using the `order_events` routing key. Inventory declares and consumes the `order_events` queue with dead-letter settings:

```text
order_events
  └─ rejected message (requeue=False)
       └─ dlx exchange
            └─ order_events_dlq
```

RabbitMQ queue settings are immutable after a queue is created. If you change the declared arguments for `order_events`, delete only that local queue in RabbitMQ Management before restarting the stack. This discards messages that were waiting in that queue, so do it only in this learning environment.

## Logs with Loki and Grafana

Promtail reads Docker container logs through the read-only Docker socket and pushes them to Loki. The destination in `promtail-config.yaml` is:

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
```

If Grafana Explore shows no containers, first inspect Promtail:

```bash
docker compose logs promtail
```

Then restart it after a configuration change:

```bash
docker compose up -d --force-recreate promtail
```

In Grafana Explore, choose Loki and use:

```logql
{container=~".+"}
```

## Kubernetes with Minikube

Install the host tools once on macOS:

```bash
brew install kubectl minikube
```

Start the local cluster through Docker Desktop:

```bash
minikube start --driver=docker
kubectl get nodes
```

Build the current User service image in Minikube’s Docker environment and apply the manifest:

```bash
eval $(minikube docker-env)
docker build -t user-service:latest -f services/user-service/Dockerfile .
kubectl apply -f k8s/user-api.yaml
```

Inspect and access it:

```bash
kubectl get deployments,pods,services
kubectl logs deployment/user-service-deployment
minikube service user-service --url
```

The `k8s/user-api.yaml` manifest deliberately covers only the User service at this point in the tutorial. Its SQLite configuration and two replicas are for Kubernetes learning; it is not a Kubernetes version of the whole Compose stack yet.

Remove only the current Kubernetes tutorial resources when you are finished:

```bash
kubectl delete -f k8s/user-api.yaml
```

Stop the local cluster later if needed:

```bash
minikube stop
```

## Common issues

| Symptom | First check |
| --- | --- |
| `kubctl: command not found` | The command is spelled `kubectl`; install it with Homebrew if needed. |
| `minikube: command not found` | Install it with `brew install minikube`. |
| Kubernetes pod says `ImagePullBackOff` | Run `eval $(minikube docker-env)`, rebuild `user-service:latest`, then recreate the deployment. |
| Docker service cannot find `fastapi` | Rebuild with `docker compose up --build`; `.dockerignore` keeps a Mac virtual environment out of Linux containers. |
| RabbitMQ `PRECONDITION_FAILED` on `order_events` | A queue already exists with different immutable arguments; inspect and delete that learning queue before restarting. |
| Grafana shows no containers | Check `docker compose logs promtail` and confirm the `clients` URL points to `http://loki:3100/loki/api/v1/push`. |

## License and attribution

This project is licensed under the [MIT License](LICENSE). Copyright © 2026 Vedant Nilesh Shinde.