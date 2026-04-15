# Academic Service

FastAPI-based academic core service for academic years, semesters, subjects, classes, and class-student assignment.

## Commands

Install dependencies:

```bash
poetry install
```

Run the service:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

Health endpoints:

```text
http://localhost:8002/api/health
http://localhost:8002/api/ready
```

Initialize Aerich:

```bash
poetry run aerich init
poetry run aerich init-db
```

Create a migration after model changes:

```bash
poetry run aerich migrate
poetry run aerich upgrade
```
