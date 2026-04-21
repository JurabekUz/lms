# LMS Microservices Learning Plan (gRPC + RabbitMQ)

Bu repo — microservice arxitekturasini amaliy o‘rganish uchun “real” LMS skeleton.
Maqsad: katta kodbazalarni tez tushunish, service boundary’larni ajratish, servislar orasida to‘g‘ri bog‘lanish (sync/async), va productionga yaqin muammolar (reliability, observability, versioning) bilan ishlash.

## 1) Goal & Why

Biz nimani o‘rganamiz:

- Katta loyihalarda “qayerdan boshlash”: service map, data ownership, API contract.
- Service boundary: har bir servis nimaga javobgar (ownership).
- Synchronous integratsiya: REST (Stage 1).
- Asynchronous integratsiya: RabbitMQ + event-driven (Stage 2).
- Strongly typed contract: gRPC (Stage 2, selective).
- Real-world patterns: idempotency, retries, DLQ, outbox, schema evolution.
- Debug & observability: request_id/correlation_id, log standardlari.

“Learning-first” prinsip:

- Avval REST bilan oqimlar ishlasin.
- Keyin broker/gRPC qo‘shamiz — faqat haqiqiy manfaat bergan joylarda.

## 2) Current State (Repo Snapshot)

Hozirgi servislar:

- `services/identity_service`:
  - login (JWT issue)
  - users/roles
  - JWT ichida `school_id` claim bo‘lishi mumkin (multi-tenant yo‘nalish)
- `services/academic_service`:
  - academic-year/semester/subject/class/class-student
  - domain model’larda `school_id` bor

Hozirgi aloqa:

- REST + Swagger/OpenAPI (har service o‘zida)
- Broker yo‘q
- gRPC yo‘q

## 3) Service Boundaries (Ownership)

**Identity Service owns**

- Authentication (login/refresh), token lifecycle
- User lifecycle (create/disable)
- Roles/permissions
- User ↔ school/tenant bog‘liqligi (school membership source of truth)

**Academic Service owns**

- Academic struktura: academic-year, semester, subject, class, enrollment/assignment
- Har bir yozuv `school_id` bilan scoped bo‘lishi shart
- Identity’ga faqat `user_id` kabi external reference saqlaydi

Qoidalar:

- Cross-service DB join yo‘q.
- Cross-service foreign key yo‘q.
- Integratsiya faqat: API (REST/gRPC) yoki event (RabbitMQ) orqali.

## 4) Communication Strategy

**Sync (Stage 1 — REST)**

- “Immediate UX kerak” bo‘lgan joylar:
  - login
  - user bo‘lishini tekshirish (zarur bo‘lsa)
  - permission check (kutilsa)

**Async (Stage 2 — RabbitMQ)**

Eventual consistency bo‘lishi mumkin bo‘lgan use case’lar:

- audit log
- notification triggers (email/SMS)
- reporting/analytics read-model
- cache warmup / denormalized views

**Selective gRPC (Stage 2)**

gRPC’ni “hamma joyda” emas, faqat kuchli contract va performance kerak joyda:

- internal user lookup
- permission check
- high-volume read APIs

## 5) RabbitMQ Stage (Stage 2)

### 5.1 Topology (proposed)

- Exchange: `lms.events` (type: `topic`)
- Routing keys (misollar):
  - `identity.user.created`
  - `identity.user.updated`
  - `identity.user.deactivated`
  - `academic.class.created`
  - `academic.class_student.assigned`
- Queues (misollar):
  - `audit.q` binds `#`
  - `notifications.q` binds `identity.user.*` va kerakli academic eventlar
  - `reporting.q` binds `academic.#`
- DLQ (misollar):
  - `audit.dlq`, `notifications.dlq`, `reporting.dlq`

### 5.2 Event Envelope (JSON + version)

Standart event envelope:

```json
{
  "event_id": "uuid",
  "event_type": "identity.user.created",
  "event_version": 1,
  "occurred_at": "2026-04-22T10:00:00Z",
  "producer": "identity-service",
  "correlation_id": "uuid-or-request-id",
  "payload": {
    "school_id": "uuid",
    "user_id": "uuid",
    "username": "alice"
  }
}
```

Qoidalar:

- `event_id` idempotency uchun.
- `event_version` schema evolution uchun.
- `correlation_id` tracing/log correlation uchun.
- `payload` ichida `school_id` bo‘lishi kerak (agar event school scoped bo‘lsa).

### 5.3 Reliability Rules

- Delivery: **at-least-once**
- Consumer: **idempotent** (bir event qayta kelsa ham natija bir xil bo‘lsin)
- Retry: exponential backoff (limited attempts)
- Poison messages: DLQ
- Consumer code: “fail fast + safe retry” (validation, schema checks)

### 5.4 Outbox Pattern (recommended milestone)

Producer’da transaction ichida:

1. Business write (masalan `User.create`)
2. `outbox` jadvalga event yozish (`event_id`, `event_type`, `payload`, `sent_at=null`)

Background publisher:

1. `sent_at is null` eventlarni o‘qiydi
2. RabbitMQ’ga publish qiladi
3. `sent_at` ni belgilaydi

Natija:

- Producer crash bo‘lsa ham event yo‘qolmaydi.
- Duplicate publish bo‘lishi mumkin → consumer idempotency bilan hal qiladi.

## 6) gRPC Stage (Stage 2)

### 6.1 First gRPC Candidate: IdentityQuery (read-only)

RPC’lar:

- `GetUserById(user_id) -> User`
- `CheckPermission(user_id, permission) -> Allowed`

### 6.2 Contract location

- `.proto` fayllar: `packages/contracts/proto/`
- Har service o‘zida generated client/server stublar
- Runtime’da shared business code yo‘q (faqat contract shared)

### 6.3 Auth in gRPC

- Metadata: `authorization: Bearer <jwt>`
- Identity service token’ni tekshiradi (Stage 2 learning uchun shared secret ok)

## 7) What to Add (New services to practice)

Stage 2 uchun amaliy servislar:

- `audit_service` (consumer): `lms.events` dan hamma eventni olib, immutable audit log yozadi
- `notification_service` (consumer): user/class eventlar → email/SMS trigger (stub ham bo‘ladi)
- `reporting_service` (consumer): per `school_id` reporting read-model (denormalized)

Optional Stage 3:

- `api_gateway` / BFF

## 8) Microservice Must-Know Checklist

- Contract versioning:
  - OpenAPI: breaking changes yo‘q (additive changes preferred)
  - Events: `event_version` + backward compatibility
  - gRPC: proto evolution rules
- Observability:
  - `request_id` / `correlation_id`
  - structured logging
- Resilience:
  - timeouts
  - retries (bounded)
  - graceful degradation
- Data ownership:
  - each service owns its DB
  - integration via API/events
- Idempotency + DLQ mindset

## 9) Roadmap (with Acceptance Criteria)

### Stage 1 — REST stable, school scoping works

AC:

- Academic endpoints faqat caller’ning `school_id` scope’ida ishlaydi (create/list/read).
- JWT’dan `school_id` olib, Academic DB row’larda mos `school_id` yoziladi.

### Stage 2A — RabbitMQ local + 1 producer + 1 consumer

AC:

- `identity.user.created` publish qilinadi.
- `audit_service` eventni consume qilib DB’ga yozadi.
- Duplicate delivery bo‘lsa ham audit log duplicate bo‘lmaydi (idempotent).

### Stage 2B — Outbox in one producer

AC:

- Producer crash/restart bo‘lsa ham event keyin publish bo‘ladi.
- “No loss” (business write bo‘lsa, outbox’da event bor).

### Stage 2C — First gRPC internal query

AC:

- Academic service optional ravishda IdentityQuery gRPC orqali user existence check qiladi.
- Timeout qo‘yilgan; Identity down bo‘lsa Academic degrade qiladi (product decision).

### Stage 3 — Observability + schema evolution drills

AC:

- Correlation ID end-to-end ko‘rinadi (logs).
- Event schema version bump test qilingan.

## 10) Local RabbitMQ (minimal)

Learning uchun management UI bilan:

```bash
docker run --rm -it \
  -p 5672:5672 -p 15672:15672 \
  --name lms-rabbit \
  rabbitmq:3-management
```

Default login:

- user: `guest`
- pass: `guest`
- UI: `http://localhost:15672`

