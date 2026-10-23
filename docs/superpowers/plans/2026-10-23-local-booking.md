# StudySpace Local Booking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. User explicitly requested implementation now; execute inline and retain a final independent review.

**Goal:** Deliver the locally deployed, trilingual reservation application and upload the tested source to the existing GitHub repository.
**Architecture:** FastAPI modular monolith; SQLAlchemy/Alembic SQLite schema; serialized writes with BEGIN IMMEDIATE; React UI on the same origin using HttpOnly sessions. Existing coursework and old API contract are historical.
**Tech Stack:** React 18, TypeScript, Vite, FastAPI, SQLAlchemy 2, Alembic, SQLite; standard-library scrypt/session secrets.
**Spec:** docs/superpowers/specs/2026-10-23-local-booking-design.md

## Global Constraints

- Only local accounts, no real university identity verification; FR-022/TC-038 retired, no fake VERIFIED.
- Bind 127.0.0.1; use existing package-lock.json/uv.lock; secrets and runtime DB stay ignored.
- Business timezone Asia/Shanghai; [start,end), 30-minute boundaries, 08:00–22:00 default, 7 natural-day default, maximum 24h; multiple non-overlapping bookings allowed.
- Chinese/Russian formal documents, zh-CN/ru-RU/en-US UI. Preserve stable IDs, historical coursework and existing repository history.
- Work on feature/local-booking-mvp. Push authorized; merging main is not authorized.

## Review Focus

- Two simultaneous bookings for the same seat/user must not both succeed; task 2 tests real concurrent requests and separate DB connections.
- Timezone and exact midnight boundaries must be checked server-side; task 2 uses literal Shanghai/UTC fixtures and invalid offset/day examples.
- Privilege changes and resource shutdown racing a reservation must recheck inside the write lock; task 3 tests revoked sessions, last admin and cancellations.
- A failed/stale frontend response must not leave a false success or wipe a newer search; task 4 tests error states and request cancellation.
- Fresh clone startup, persisted DB restart and restoration must work without external services; task 5 runs migration/backup/restore CLI and packaged single-origin startup and local Docker Compose.

### Task 1: Local accounts, schema and sessions
**Files:** backend/app/models.py, schemas.py, security.py, api.py; backend/migrations; backend/alembic.ini; backend/app/main.py, config.py, database.py; backend/tests/test_local_accounts.py; docs/data and formal local-scope document.
**Interfaces:** request_user(request, db) -> User; write_session(request) -> Session; POST /api/v1/auth/register, /login, /logout; GET /api/v1/auth/me. Cookie studyspace_session; public registration forbids role.
- [x] Add integration tests for local register/login/logout, duplicate casefolded username, forbidden role/Origin/header and disabled-session revocation; watch 404 failures.
- [x] Add Alembic initial schema, scrypt passwords, hashed expiring sessions and generic validation errors; no automatic schema writes in health.
- [x] Run account tests and complete Python suite; update intentionally superseded foundation API/version expectations. Commit.

### Task 2: Resources and atomic reservation
**Files:** backend/app/booking.py, api.py, schemas.py; backend/tests/test_bookings.py.
**Interfaces:** GET /rooms, /rooms/{id}/seats; POST /bookings; GET /bookings; POST /bookings/{id}/cancel. All dates aware in requests, UTC storage; client-visible errors use stable codes.
- [x] Add tests for available seats, ownership, adjacency, repeated cancellation, user/seat overlap, date/hour/granularity/timezone boundaries; observe missing behavior.
- [x] Implement validation and queries in locked transactions; never trust available-seat results as a lock.
- [x] Run concurrent same-seat and same-user requests (exactly one 201), plus non-overlapping requests (both 201), and full Python suite. Commit.

### Task 3: Administrative management and lifecycle
**Files:** backend/app/admin.py, maintenance.py, cli.py; backend/tests/test_admin.py, test_maintenance.py.
**Interfaces:** /admin/rooms, /admin/seats, /admin/opening-exceptions, /admin/policy, /admin/users, /admin/bookings, /admin/statistics; CLI init-local, create-admin, cleanup, backup, restore.
- [x] Write failures for role access, unique seats, disabling resources/users, shrinking schedules, last admin, statistics and pagination.
- [x] Implement minimal admin services and atomic cancellation/audit; configurable date exceptions and 1–7 day advance window.
- [x] Write and run CLI tests for idempotent demo seeding, migration roundtrip, no default admin, backup/restore into a new file and retention cleanup.
- [x] Run complete Python suite and commit.

### Task 4: Trilingual booking UI
**Files:** frontend/src/App.tsx, styles.css, api/client.ts, i18n.ts; views/{Auth,Rooms,Bookings,Admin}.tsx; frontend/src/App.test.tsx.
**Interfaces:** JSON API and same-origin cookies above; X-StudySpace-Request: 1. Public resources, session recovery, student/admin navigation, no tokens in browser storage.
- [x] Write failures for login/register, search selection, conflict/error recovery, cancel and language selection.
- [x] Implement library-style responsive UI, room filters/date/start/end, seats, confirmation, personal records, admin forms/filters, loading/error/empty states and accessible labels.
- [x] Run full Vitest, ESLint, TypeScript and build; commit.

### Task 5: Local deployment and current documentation
**Files:** compose.yaml, backend/Dockerfile, frontend/Dockerfile, scripts/start_local.sh, scripts/local.sh, scripts/check.sh; backend/app/main.py/static hosting; README.md, REPORT.md, docs/zh-CN/18_Local_Version.md, docs/ru-RU/18_Local_Version.md, runtime OpenAPI and evidence.
- [x] Build and run actual local Docker Compose with a persistent SQLite volume and automatic upgrade/seed, and verify restart persistence; preserve native startup.
- [x] Test fresh initialization/start behavior and SPA/API separation; implement single-port build serving and loopback-only launch.
- [x] Format legacy script lint without changing business behavior, run full checks and record actual results.
- [x] Run real local browser student/admin flows and 375/768/1440 captures; fix reproducible failures with tests.
- [x] Update scope/traceability/current report based on actual test coverage; historical materials retain their dates. Commit.

### Task 6: Review and GitHub delivery
**Files:** delivery evidence and report.
- [x] Independent whole-branch review against spec and plan; fix Important/Critical findings with failing regression tests.
- [x] Run final complete checks, inspect actual committed files for secrets/databases, verify local startup.
- [ ] Push feature/local-booking-mvp, create and attach PR to main, verify remote commit/file state. Leave main merge and teacher/student claims pending.
