# Audit Service

FastAPI-based audit service that consumes RabbitMQ events and stores immutable audit logs.

## Commands

Install dependencies:

```bash
poetry install
```

Run the service:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

Health endpoints:

```text
http://localhost:8003/api/health
http://localhost:8003/api/ready
```
