# LMS Monorepo

Monorepo for a startup-stage LMS built with FastAPI, Tortoise ORM, PostgreSQL, and Poetry.

## Services

- `services/identity_service`
- `services/academic_service`
- `services/audit_service`

## Stage 2 local stack

Start RabbitMQ + Postgres for identity/audit:

```bash
docker compose -f docker-compose.stage2.yml up -d
```

RabbitMQ management UI:

- `http://localhost:15672`
- user: `guest`
- pass: `guest`

## Current status

- PRD and engineering rules are documented in `docs/`
- Microservices learning roadmap is in `docs/LEARNING_PLAN.md`
- identity and academic services are separate FastAPI apps
- Stage 2A foundation is added: identity producer + audit consumer
