# NextGen LMS PRD

## 1. Product Summary

NextGen LMS is a startup-stage learning management platform for schools. The first milestone focuses on two backend services:

1. Identity Service
2. Academic Core Service

The product must move fast in early delivery, but the architecture should not block future growth into multi-tenant school management.

## 2. Product Goals

- Build a clean backend foundation that can grow from one school to many schools.
- Keep user identity and academic structure separate so each service can scale independently.
- Support flexible school scheduling where lessons, training, meals, and similar activities share one timetable model.
- Let the team ship quickly without overengineering the first version.

## 3. Non-Goals For V1

- Full event-driven architecture across every operation
- Complex CQRS or distributed sagas
- Service mesh or Kubernetes-first deployment
- Highly customized reporting and analytics
- Real-time classroom collaboration features

## 4. Target Users

- Platform Administrator
- School Director
- Teacher
- Student
- Parent

## 5. Scope Of V1

### Identity Service

Responsibilities:

- Authentication by username/password
- JWT issuing and validation
- User lifecycle management
- Role and permission management
- Profile management
- Teacher-specific extra data

Core entities:

- `users`
- `roles`
- `profiles`
- `teacher_data`

### Academic Core Service

Responsibilities:

- Academic year management
- Semester management
- Class management
- Subject/activity management
- Homeroom teacher assignment
- Student assignment into classes

Core entities:

- `academic_years`
- `semesters`
- `classes`
- `subjects`
- `class_students`

## 6. Functional Requirements

### Identity

- `REQ-01`: Users can log in with username and password.
- `REQ-02`: Successful login returns access token and refresh token.
- `REQ-03`: Admin can create, update, deactivate, and reactivate users.
- `REQ-04`: Admin can assign roles to users.
- `REQ-05`: Admin can manage dynamic profile metadata without schema changes for every small business change.
- `REQ-06`: Teacher-specific data is stored separately from generic profile data.

### Academic Core

- `REQ-07`: Director can monitor academic structure and operational data, but does not create or manage academic years, semesters, subjects, or classes.
- `REQ-08`: School admin can create academic years with a start date and an end date.
- `REQ-09`: School admin can create semesters under an academic year, and each semester has a start date and an end date.
- `REQ-10`: School admin can create subject records used in scheduling.
- `REQ-11`: Subjects support categories such as regular classes, extracurricular activities, meals, and future extensions because all of them appear in the schedule.
- `REQ-12`: School admin can create classes and assign a homeroom teacher to each class.
- `REQ-13`: School admin can assign students to classes.

### Cross-Service

- `REQ-14`: Academic Core stores only identity references such as `student_id`, `teacher_id`, `homeroom_teacher_id`, or `created_by`.
- `REQ-15`: Client-facing systems may hydrate user display data by calling Identity Service directly or through an API gateway/BFF.

## 7. Non-Functional Requirements

- API style: REST first
- Internal communication: REST first, gRPC later when justified
- Database: PostgreSQL per service
- Framework: FastAPI
- ORM: Tortoise ORM
- Package management: Poetry
- Migration approach: Tortoise migration tooling only
- Service isolation: each service owns its own database schema
- Auth model: JWT-based
- Observability baseline: structured logs, health check, request ID, error tracking hooks

## 8. Recommended Data Model Notes

### Good choices in your draft

- Separating Identity from Academic Core is correct.
- Storing only `user_id` references in Academic Core is correct.
- Using profile metadata for flexible startup fields is reasonable.
- Treating meals/training/lessons under a shared scheduling concept is a strong idea.

### Changes I recommend

1. Do not put all permissions into a single JSONB field forever.
   Use JSONB in V1 if you want speed, but design so you can later move to `permissions`, `role_permissions`, and `user_roles` tables.

2. Avoid a single `role_id` on `users`.
   Real schools often need multiple roles for one person, like `Teacher + Parent` or `Admin + Teacher`.
   Better model:
   - `roles`
   - `user_roles`

3. Be careful with generic `metadata`.
   Flexible metadata is useful, but do not store core searchable business fields only in JSONB.
   Example:
   - good in JSONB: hobbies, notes, optional preferences
   - better as columns: first name, last name, birth date, phone

4. `subjects` may be too narrow as a name if it includes meals.
   Better options:
   - keep `subjects` and add `type`
   - or rename later to `activities`
   For V1, `subjects` with `type` is acceptable if the team understands the meaning.

5. If you now use `semesters` instead of `terms`, keep the same validation idea.
   Add rules so date ranges are valid and do not overlap in ways your business does not allow.

6. `classes` should explicitly store a `homeroom_teacher_id`.
   That is a core business field and should not live only inside flexible metadata.

7. Student-to-class membership should be modeled explicitly.
   A dedicated relation such as `class_students` is clearer than burying student IDs inside JSON or overloading a generic enrollment table too early.

## 9. Three-Layer Architecture Rule

Each service should follow a 3-layer structure:

1. Presentation layer
   FastAPI routers, request/response schemas, auth dependencies

2. Application layer
   Use cases, service logic, orchestration, validation of business rules

3. Infrastructure layer
   Tortoise models, repositories, external clients, message broker adapters

Rule:
API handlers should not directly contain business logic or ORM queries.

## 10. Suggested V1 Service Boundaries

### Service 1: Identity Service

Owns:

- authentication
- user account lifecycle
- role assignments
- profile data

Does not own:

- classes
- academic years
- enrollments

### Service 2: Academic Core Service

Owns:

- academic structure
- subject/activity catalog
- class membership records
- homeroom teacher assignments

Does not own:

- passwords
- login sessions
- role definitions

## 11. API Direction

Start simple:

- external APIs: REST/JSON
- internal sync communication: REST/HTTP
- async integration: message queue only for important domain events

Recommended first events:

- `user.created`
- `user.deactivated`
- `student.enrolled`
- `class.created`

## 12. Risks

- Too much flexibility in JSONB may create weak validation and messy reporting.
- Too many microservices too early may slow a startup more than help it.
- Using microservices without observability, contracts, and local-dev tooling can become painful fast.

## 13. Delivery Recommendation

Phase 1:

- build as a monorepo
- create two independent FastAPI apps
- one database per service
- synchronous REST between services
- JWT auth
- shared internal package only for safe cross-cutting code such as logging, config, and common exceptions

Phase 2:

- introduce a message broker
- publish domain events
- add API gateway or BFF
- evaluate gRPC for internal high-traffic or strongly typed contracts

Phase 3:

- multi-tenancy support
- audit logs
- outbox pattern
- stronger permission system

## 14. Final Evaluation Of Your Current Plan

You are not wrong. Your foundation is good.

The main corrections are:

- prefer `user_roles` over single `role_id`
- use JSONB carefully, not for important relational data
- start with REST before gRPC
- add a message queue only when you have a real async workflow
- keep microservices count small at the beginning

If your goal is both shipping product and learning microservices, two services is the right starting point.
