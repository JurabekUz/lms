# LMS Monorepo

Monorepo for a startup-stage LMS built with FastAPI, Tortoise ORM, PostgreSQL, and Poetry.

## Services

- `services/identity_service`
- `services/academic_service`

## Current status

- PRD and engineering rules are documented in `docs/`
- Microservices learning roadmap is in `docs/LEARNING_PLAN.md`
- monorepo skeleton is created
- identity and academic services are being built as separate FastAPI apps inside the monorepo

## Next steps

1. install dependencies with Poetry
2. configure PostgreSQL databases
3. generate first migrations
4. implement auth and academic use cases
