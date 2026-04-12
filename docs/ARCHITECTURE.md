# Architecture Guide

## 1. Recommended Starting Architecture

You want both product progress and microservice experience. The right compromise is:

- monorepo
- two services
- separate databases
- REST between services
- message queue introduced later

This gives you real microservice practice without making local development too heavy.

## 2. Initial Service Map

### Identity Service

Endpoints may include:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `POST /api/v1/roles`
- `POST /api/v1/users/{user_id}/roles`

### Academic Core Service

Endpoints may include:

- `POST /api/v1/academic-years`
- `POST /api/v1/terms`
- `POST /api/v1/classes`
- `POST /api/v1/subjects`
- `POST /api/v1/enrollments`
- `GET /api/v1/classes/{class_id}/students`

## 3. Suggested Internal Folder Shape Per Service

```text
services/identity_service/
  app/
    api/
    application/
    domain/
    infrastructure/
    main.py
  pyproject.toml
```

Notes:

- `domain/` may stay lightweight in V1
- if full domain layering feels heavy, keep strong separation between `api`, `application`, and `infrastructure`

## 4. Example Request Flow

Create enrollment flow:

1. client calls Academic Core API
2. Academic Core validates class and term
3. Academic Core verifies `student_id` format
4. optionally Academic Core asks Identity Service whether user exists and is active
5. Academic Core creates enrollment
6. Academic Core may publish `student.enrolled` event later

## 5. Message Queue Strategy

Introduce a broker after synchronous flows are stable.

Good first async use cases:

- audit log events
- notification triggers
- profile changes cached in another service
- analytics or reporting pipelines

Do not use a queue first for:

- login flow
- simple create/read operations
- anything that your core UX needs immediately

## 6. gRPC Strategy

gRPC is useful, but not a first step.

Use REST first because:

- it is easier to debug
- easier in Swagger/OpenAPI
- simpler while requirements are changing fast
- better for learning basic service boundaries first

Learn gRPC after your REST version works.

Best first gRPC candidates:

- internal user lookup service
- permission check service
- high-volume internal read APIs

## 7. Multi-Tenancy Direction

Do not fully optimize for multi-tenancy in V1, but do not block it.

Safe preparation:

- design APIs with school/tenant awareness
- reserve `tenant_id` in important models if needed soon
- avoid assuming global uniqueness of business data like class names

## 8. Shared Package Rule

Allowed in `packages/common`:

- config helpers
- logging utilities
- shared exception base classes
- shared auth token parsing utilities if carefully designed

Not allowed in `packages/common`:

- service business rules
- ORM models reused across services
- cross-service repository logic

## 9. Media And Attachments

Files, documents, and images are important enough to deserve their own ownership boundary.

Recommended rule:

- do not create a shared `media` table inside `identity_service`
- do not use cross-service foreign keys
- let a future `media_service` or `attachment` module own file metadata and storage concerns
- other services should store only external references such as `media_id`

Example:

- `profiles.avatar_media_id`
- `assignments.attachment_media_id`
- `submissions.file_media_id`

This keeps Identity focused on identity, while media ownership stays reusable across the LMS.

## 10. Local Development Recommendation

Start with:

- one PostgreSQL instance with separate databases
- two FastAPI services
- optional local broker container later

You do not need Kubernetes to learn microservices well at this stage.

## 11. What You Were Right About

- Users/Auth should be separated from Academic structure.
- Academic service should only store external identity references.
- Startup speed matters as much as architecture quality.
- Flexible scheduling model is a strong product choice.

## 12. What To Adjust

- use multiple roles per user
- be disciplined with JSONB
- do not add too many services too early
- keep gRPC and broker as stage 2 learning goals, not day 1 dependencies

## 13. Practical Roadmap

### Stage 1

- monorepo setup
- Poetry setup
- base FastAPI app template
- Identity Service
- Academic Core Service
- PostgreSQL databases

### Stage 2

- shared logging and config package
- service-to-service auth
- integration tests
- Docker Compose local environment

### Stage 3

- message broker
- domain events
- outbox pattern
- API gateway or BFF

### Stage 4

- selective gRPC introduction
- tracing
- rate limiting
- tenant-aware architecture expansion
