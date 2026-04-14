# Identity Service

FastAPI-based identity service for users, roles, profiles, and authentication.

This service also mounts a `fastapi-admin` backoffice at `/admin`.

## Commands

Install dependencies:

```bash
poetry install
```

Run the service:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

Open the admin:

```text
http://localhost:8001/admin
```

Initialize the first admin account:

```text
http://localhost:8001/admin/init
```
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
