# Engineering Rules

## 1. Core Principles

- Build for clarity first, then scale.
- Prefer boring and reliable choices in V1.
- Every service must have a clear ownership boundary.
- Shared code must be minimal to avoid hidden coupling.
- Business logic belongs in the application layer, not routers and not ORM models.

## 2. Monorepo Rules

Monorepo is the correct choice for your stage.

Use this structure:

```text
lms/
  services/
    identity_service/
    academic_service/
  packages/
    common/
  docs/
  pyproject.toml
  lms.code-workspace
```

Rules:

- each service is independently runnable
- each service has its own config, API, domain logic, and database models
- `packages/common` may contain only low-risk shared utilities
- never place business logic shared across services unless it is truly cross-cutting and stable

## 3. FastAPI 3-Layer Design

### Presentation Layer

Contains:

- routers
- request and response schemas
- dependency injection setup
- auth dependency adapters

Must not contain:

- raw ORM queries
- transaction coordination
- business rules beyond trivial input formatting

### Application Layer

Contains:

- use cases
- business services
- validation of domain rules
- transaction boundaries
- orchestration across repositories and clients

### Infrastructure Layer

Contains:

- Tortoise ORM models
- repository implementations
- database initialization
- external HTTP/gRPC clients
- broker producers/consumers

## 4. Coding Rules

- Python version should be pinned consistently across services.
- Use type hints everywhere in application code.
- Use Pydantic for API contracts.
- Use small service classes or use-case handlers instead of giant utility modules.
- Prefer explicit names like `CreateUserUseCase` over vague names like `Manager`.
- Keep functions short and responsibility-focused.
- Raise domain-specific exceptions and translate them at the API layer.

## 5. Tortoise ORM Rules

- Tortoise ORM is acceptable for your learning and startup pace.
- Use one database per service.
- Do not allow cross-service database access.
- Keep Tortoise models in infrastructure, not mixed with API schemas.
- Use Tortoise migration tooling consistently and never do manual schema drift.

Important note:

Tortoise itself is not the migration system. You will still need its migration tooling workflow.
In practice this usually means using the Tortoise-compatible migration tool you standardize on inside the repo. The important rule is: do not introduce a second ORM or unrelated migration stack.

## 6. API Rules

- Version APIs from the start, for example `/api/v1`.
- Every service exposes `/health` and `/ready`.
- Return structured error responses.
- Use cursor or limit/offset pagination for list endpoints.
- Validate UUIDs, enums, and dates strictly at the API boundary.

## 7. Auth And Identity Rules

- Identity Service is the single source of truth for user credentials.
- Other services may store only user references such as `user_id`.
- Prefer multi-role support with `user_roles`.
- Separate auth credentials from human profile data.
- Avoid leaking internal role structure directly to public clients without a stable API contract.

## 8. Data Rules

- Use normal columns for important filterable fields.
- Use JSONB only for optional, low-structure extensions.
- Add timestamps to every main table: `created_at`, `updated_at`.
- Use soft delete only when there is a real business need.
- Decide early whether tenant isolation will use `tenant_id` on all tables or database-per-tenant later.
- If a record refers to a file owned by another service, store only a reference like `media_id`, not a database foreign key.

## 9. Communication Rules

Start with:

- REST for synchronous service-to-service calls
- message queue for asynchronous domain events only when needed

Do not start with:

- gRPC everywhere
- event-driven everything
- complex distributed transactions

Use gRPC later if:

- you need strongly typed internal contracts
- you have high-throughput internal calls
- you want streaming

Recommended message queue learning path:

1. Redis streams or RabbitMQ for learning simplicity
2. Kafka later if scale and event retention really justify it

## 10. Observability Rules

Every service should include:

- structured logging
- request ID / correlation ID
- centralized config loading
- health checks
- startup and shutdown logging

Later add:

- metrics
- tracing
- error monitoring

## 11. Testing Rules

- Unit test application-layer business logic first.
- Add API integration tests for critical endpoints.
- Add contract tests for service-to-service interfaces.
- Do not rely only on manual Swagger testing.

Minimum required tests for each new feature:

- happy path
- one validation failure
- one authorization or permission failure

## 12. Delivery Rules

- Ship in thin vertical slices.
- Do not build all services fully before integrating.
- Prefer one working user flow end-to-end over many half-finished modules.

Recommended first end-to-end slice:

1. create user
2. login
3. create academic year
4. create class
5. enroll student by `user_id`

## 13. VS Code Workspace Rules

- keep service folders visible in one workspace
- add per-service `.env.example`
- standardize formatter and linter settings early
- define common launch and debug profiles for FastAPI apps
- keep onboarding docs in `docs/`

## 14. Decision Summary

For your current stage, this is the senior-level path:

- yes to monorepo
- yes to two services
- yes to FastAPI 3-layer architecture
- yes to Tortoise ORM
- yes to Poetry
- no to many microservices at the start
- no to gRPC as the first communication layer
- no to storing too much business data in JSONB
