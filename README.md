# Fast Store

Fast Store is a learning project that demonstrates a small, containerised FastAPI microservices system. It uses synchronous REST, gRPC, asynchronous RabbitMQ events, a dead-letter queue, distributed tracing, centralised logs, and an introductory Kubernetes deployment.

## What is in the project?

| Component | Responsibility | How it communicates |
| --- | --- | --- |
| User service | User APIs, authentication, and purchase lookup | REST, PostgreSQL, gRPC to product service |
| Product service | Product information | gRPC |
| Order service | Accepts orders and publishes `OrderPlaced` events | REST, RabbitMQ |
| Inventory service | Consumes order events and updates mock inventory | RabbitMQ |
| RabbitMQ | Event broker and dead-letter queue host | AMQP |
| Traefik | Routes public user-service HTTP requests | HTTP |
| Jaeger | Shows distributed traces | OpenTelemetry |
| Loki + Promtail + Grafana | Collects and explores container logs | Docker logs / LogQL |

The order-to-inventory flow is:

```text
Client -> Order service -> RabbitMQ (order_events) -> Inventory service
                                                    -> DLX -> order_events_dlq on rejection
```

## Prerequisites

- Docker Desktop, running
- [uv](https://docs.astral.sh/uv/) for local Python work
- Python 3.12 (the project version)

For the Kubernetes section only, also install `kubectl` and Minikube:

```bash
brew install kubectl minikube
```

## Run with Docker Compose

From the project root:

```bash
docker compose up --build
```

To run it in the background:

```bash
docker compose up --build -d
```

To stop the stack without removing the PostgreSQL data volume:

```bash
docker compose down
```

## Open the running services

| Service | Address | Notes |
| --- | --- | --- |
| User service API docs | [http://localhost/docs](http://localhost/docs) | Routed through Traefik |
| Order service API docs | [http://localhost:8002/docs](http://localhost:8002/docs) | Place orders here |
| Inventory service API docs | [http://localhost:8003/docs](http://localhost:8003/docs) | Check mock inventory |
| RabbitMQ Management | [http://localhost:15672](http://localhost:15672) | Login: `guest` / `guest` |
| Jaeger | [http://localhost:16686](http://localhost:16686) | Trace viewer |
| Grafana | [http://localhost:3000](http://localhost:3000) | Login: `admin` / `admin` |
| Traefik dashboard | [http://localhost:8080/dashboard/](http://localhost:8080/dashboard/) | Development dashboard |

## Try the event-driven flow

1. Open the Order service docs at `http://localhost:8002/docs`.
2. Call `POST /orders/` with a `product_id` and `user_id`.
3. Watch the Inventory service logs:

   ```bash
   docker compose logs -f inventory-service
   ```

`product_id=99` exists in the current mock inventory. A normal event is acknowledged after processing. The tutorial’s deliberate failure case, `product_id=999`, is rejected and routed to the `order_events_dlq` dead-letter queue in RabbitMQ.

## Explore logs in Grafana

Promtail discovers Docker containers and sends their logs to Loki. In Grafana, configure a Loki data source using this URL from inside the Compose network:

```text
http://loki:3100
```

Then open **Explore**, choose Loki, and query:

```logql
{container=~".+"}
```

Use the `container` label to narrow the results to a service.

## Kubernetes: first deployment

The current Kubernetes manifest deploys only the User service. It is deliberately an introductory step: it runs two replicas with a local SQLite database and does not yet deploy PostgreSQL, RabbitMQ, gRPC dependencies, or the observability stack to Kubernetes.

Start Minikube with Docker Desktop:

```bash
minikube start --driver=docker
```

Build the image inside Minikube’s Docker environment. This is required because the manifest uses `imagePullPolicy: Never`.

```bash
eval $(minikube docker-env)
docker build -t user-service:latest -f services/user-service/Dockerfile .
```

Deploy and inspect it:

```bash
kubectl apply -f k8s/user-api.yaml
kubectl get deployments,pods,services
minikube service user-service
```

For more development commands, ports, package-management guidance, and troubleshooting, read [DEVELOPMENT.md](DEVELOPMENT.md).

## License

This project is licensed under the [MIT License](LICENSE). Copyright © 2026 Vedant Nilesh Shinde.

## Credit

This learning project follows the FastAPI microservices tutorial series and is based on concepts demonstrated by [KNehe/fastapi-microservices](https://github.com/KNehe/fastapi-microservices). Thanks to the original author for the educational reference.
