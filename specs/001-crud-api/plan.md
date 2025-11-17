# Implementation Plan: Basic CRUD REST API for Expense Tracking

**Branch**: `001-crud-api` | **Date**: 2025-11-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-crud-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a lightweight REST API service that provides CRUD operations for expense tracking data (transactions, accounts, categories, payees). The service acts as a thin data access layer over PostgreSQL, with validation logic but no complex business rules. Database triggers handle account balance calculations and data integrity. Technical approach: Python with FastAPI for REST endpoints, SQLAlchemy for database operations, and Pydantic for request/response validation.

## Technical Context

**Language/Version**: Python 3.11 (or 3.12 if available)
**Primary Dependencies**: FastAPI (web framework), SQLAlchemy (ORM), Pydantic (validation), psycopg2 (PostgreSQL driver), Uvicorn (ASGI server)
**Storage**: PostgreSQL 15+ (with existing schema, triggers, and foreign key constraints)
**Testing**: pytest (unit/integration), pytest-asyncio (async tests), httpx (API client testing)
**Target Platform**: Linux server (containerized with Docker for deployment)
**Project Type**: Single backend service (REST API only, no frontend in this repo)
**Performance Goals**: <200ms p95 latency for simple CRUD operations, <1s for filtered list queries, support 100 concurrent requests
**Constraints**: <500MB memory per instance, database handles business logic (triggers), no caching layer initially
**Scale/Scope**: 10,000 transactions per account, ~50 API endpoints (CRUD for 4 entities + 2 reference endpoints), ~2000-3000 LOC

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md` principles:

### Code Quality & Simplicity
- [x] Each component has single, clear responsibility
  - Router layer handles HTTP concerns (parsing, validation, status codes)
  - Service layer handles business operations (CRUD logic)
  - Model layer represents database entities
  - Each router file manages one resource type (transactions, accounts, categories, payees)
- [x] No premature abstractions planned
  - Using standard FastAPI patterns without custom frameworks
  - Direct SQLAlchemy queries instead of repository pattern (unnecessary for simple CRUD)
  - Pydantic models for validation (standard FastAPI approach)
- [x] Design choices favor boring, obvious solutions over clever ones
  - Standard REST conventions (POST/GET/PUT/PATCH/DELETE)
  - FastAPI's built-in dependency injection for database sessions
  - SQLAlchemy ORM for type-safe database access
  - Standard HTTP status codes and error responses
- [x] Implementation complexity justified if unavoidable
  - No complex patterns needed for simple CRUD operations

### Testing Standards
- [x] Test strategy defined (unit, integration, contract)
  - **Unit tests**: Individual service functions (validation logic, data transformations)
  - **Integration tests**: Full request/response cycle through FastAPI TestClient
  - **Contract tests**: OpenAPI schema validation, response format verification
- [x] Tests can be written alongside or before implementation
  - Test-first approach for validation logic (known requirements from spec)
  - Integration tests written after router setup (verify end-to-end behavior)
- [x] Test isolation and independence verified
  - Each test uses fresh database transaction (rollback after test)
  - pytest fixtures provide isolated test database
  - No shared state between tests
- [x] Critical business logic test coverage planned
  - All validation rules (FR-009 to FR-012, FR-021, FR-022, FR-041 to FR-047)
  - Pagination logic (FR-005, FR-017, FR-027, FR-035)
  - Filtering and query parameters (FR-004, FR-016, FR-026, FR-034, FR-053, FR-054)
  - Error handling for all edge cases identified in spec

### User Experience Consistency
- [x] Loading states defined for async operations >200ms
  - API endpoints return immediately (<200ms target), no long-running operations
  - Client applications handle loading states (frontend responsibility)
- [x] Error handling provides clear, actionable feedback
  - Consistent error response format (error code, message, details per FR-045)
  - Validation errors include field name and specific reason (FR-043)
  - 404 responses clearly indicate resource not found (FR-042)
  - 400 responses explain malformed request issues (FR-041)
- [x] Mobile-first responsive design approach
  - N/A for backend API (no UI in this service)
- [x] Accessibility requirements (WCAG 2.1 AA) planned
  - N/A for backend API (no UI in this service)

### Performance Requirements
- [x] API latency targets defined (<200ms p95 simple, <1s complex)
  - Simple CRUD operations: <200ms p95 (single record fetch/create/update)
  - List operations with filtering: <1s p95 (under 10,000 records)
  - Database queries optimized with proper indexes (assumed in existing schema)
- [x] Resource constraints documented (<500MB backend, <2MB frontend bundle)
  - Backend memory: <500MB per instance (FastAPI + SQLAlchemy connection pool)
  - No frontend bundle (backend only)
- [x] Monitoring and metrics strategy defined
  - FastAPI built-in request logging (request path, status code, duration)
  - Database query logging for slow query detection (>500ms)
  - Error rate tracking (5xx responses)
  - Basic health check endpoint for uptime monitoring
- [x] Performance budgets established
  - Max 50 concurrent database connections per instance
  - Pagination defaults prevent unbounded queries (limit=50, max=100)
  - Query timeout: 30 seconds (PostgreSQL statement_timeout)

### Complexity Justification
If any of the following apply, document justification:
- New external dependencies
- New abstraction layers
- Performance optimizations sacrificing readability
- Architecture changes affecting multiple modules

**External Dependencies Justification**:
- **FastAPI**: We need a modern async web framework because it provides automatic OpenAPI documentation, built-in validation with Pydantic, and high performance. Simpler alternatives like Flask were rejected because they lack async support and require additional libraries for validation and API documentation.
- **SQLAlchemy**: We need an ORM because it provides type-safe database access, connection pooling, and prevents SQL injection. Writing raw SQL was rejected because it's error-prone and lacks type safety for complex queries.
- **Pydantic**: We need schema validation because FastAPI integrates it natively for request/response validation, reducing boilerplate. Manual validation was rejected because it's tedious and error-prone for 50+ endpoints.
- **pytest**: We need a testing framework because it provides fixtures, parametrization, and async test support. Standard unittest was rejected because pytest has better ergonomics and ecosystem support.

**No additional abstraction layers**: Using FastAPI's standard three-layer pattern (router → service → model) without custom abstractions like repositories or facades.

## Project Structure

### Documentation (this feature)

```text
specs/001-crud-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── openapi.yaml     # OpenAPI 3.0 specification
├── checklists/
│   └── requirements.md  # Spec quality checklist (already created)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
ai-expense-tracker-service/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration (database URL, environment)
│   ├── database.py                # Database session management
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── transaction.py
│   │   ├── account.py
│   │   ├── category.py
│   │   ├── payee.py
│   │   ├── account_type.py
│   │   └── currency.py
│   ├── schemas/                   # Pydantic models for validation
│   │   ├── __init__.py
│   │   ├── transaction.py         # TransactionCreate, TransactionUpdate, TransactionResponse
│   │   ├── account.py
│   │   ├── category.py
│   │   ├── payee.py
│   │   ├── common.py              # PaginationResponse, ErrorResponse
│   │   └── enums.py               # TransactionType, Status, CategoryType
│   ├── routers/                   # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── transactions.py
│   │   ├── accounts.py
│   │   ├── categories.py
│   │   ├── payees.py
│   │   └── reference.py           # Account types and currencies
│   └── services/                  # Business logic (CRUD operations)
│       ├── __init__.py
│       ├── transaction_service.py
│       ├── account_service.py
│       ├── category_service.py
│       └── payee_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Shared pytest fixtures
│   ├── unit/                      # Unit tests for services
│   │   ├── __init__.py
│   │   ├── test_transaction_service.py
│   │   ├── test_account_service.py
│   │   ├── test_category_service.py
│   │   └── test_payee_service.py
│   ├── integration/               # API integration tests
│   │   ├── __init__.py
│   │   ├── test_transactions_api.py
│   │   ├── test_accounts_api.py
│   │   ├── test_categories_api.py
│   │   ├── test_payees_api.py
│   │   └── test_reference_api.py
│   └── contract/                  # OpenAPI contract validation
│       ├── __init__.py
│       └── test_openapi_compliance.py
├── pyproject.toml                 # Project metadata and dependencies (uv)
├── Dockerfile                     # Container image definition
├── .env.example                   # Environment variables template
└── README.md                      # Project setup and usage

```

**Structure Decision**: Single backend service using FastAPI's standard three-layer architecture (routers → services → models). This structure provides clear separation of concerns without over-engineering:
- **models/**: SQLAlchemy ORM classes map to database tables
- **schemas/**: Pydantic models validate API requests/responses
- **routers/**: HTTP route handlers (one file per resource type)
- **services/**: CRUD business logic (one file per resource type)
- **tests/**: Three test categories matching our test strategy

This is a greenfield project with no existing source code, so all directories will be created during implementation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations requiring justification. All complexity is justified in the "Complexity Justification" section of the Constitution Check above (external dependencies only).

## Post-Design Constitution Re-Check

**Status**: ✅ All checks passed

After completing Phase 0 (Research) and Phase 1 (Design & Contracts), re-evaluating constitution compliance:

### Code Quality & Simplicity - ✅ PASS
- **Single Responsibility**: Maintained throughout design
  - Data model separates ORM models (SQLAlchemy) from API schemas (Pydantic)
  - Three-layer architecture (routers → services → models) with clear boundaries
  - Each model file represents one entity (6 models for 6 tables)
  - Each router file handles one resource type (5 routers)
- **No Premature Abstractions**: Confirmed
  - Using standard FastAPI + SQLAlchemy patterns
  - No custom repository layer (service functions use ORM directly)
  - No custom middleware or interceptors
- **Boring & Obvious**: Validated
  - Standard REST conventions throughout OpenAPI spec
  - Conventional SQLAlchemy ORM patterns
  - FastAPI dependency injection for database sessions
  - No clever tricks or metaprogramming

### Testing Standards - ✅ PASS
- **Test Strategy**: Clearly defined in quickstart.md
  - Unit tests for service layer (validation, CRUD logic)
  - Integration tests for full API endpoints
  - Contract tests for OpenAPI compliance
- **Test Independence**: Designed for isolation
  - Pytest fixtures provide fresh database per test
  - Transaction rollback after each test
  - No shared state between tests

### User Experience Consistency - ✅ PASS
- **Error Handling**: Comprehensive error format defined
  - Consistent error response structure (code, message, details)
  - All error scenarios mapped in OpenAPI spec
  - Field-level validation errors with clear reasons
- **API Consistency**: Validated
  - All list endpoints use consistent pagination format
  - All CRUD operations follow same patterns
  - snake_case field naming throughout

### Performance Requirements - ✅ PASS
- **Latency Targets**: Achievable with design
  - Simple CRUD: <200ms (single database query + serialization)
  - Filtered lists: <1s (indexed queries + pagination limits)
- **Resource Constraints**: Within budget
  - FastAPI + SQLAlchemy: ~50-100MB base memory
  - Connection pool (20 + 30 overflow): ~50MB
  - Total estimated: ~200-300MB (well under 500MB target)
- **Scalability**: Design supports targets
  - Pagination prevents unbounded queries (max 100 items)
  - Database indexes support filtering performance
  - Stateless API enables horizontal scaling

### Design Artifacts Quality

**Research Document**:
- ✅ All technology decisions documented with rationale
- ✅ No unresolved questions
- ✅ Best practices identified for each technology

**Data Model**:
- ✅ Accurate mapping to existing database schema
- ✅ All fields from schema exposed in API
- ✅ Proper nullability based on database constraints
- ✅ Clear relationships between entities
- ✅ Validation rules mapped to Pydantic constraints

**API Contracts** (OpenAPI):
- ✅ Complete coverage of all 50+ endpoints
- ✅ Request/response schemas for all operations
- ✅ Error responses documented
- ✅ Pagination consistently defined
- ✅ Filter parameters documented

**Quickstart Guide**:
- ✅ Step-by-step implementation roadmap
- ✅ Clear validation checkpoints
- ✅ Common issues & solutions
- ✅ Testing strategy outlined

### Complexity Assessment Post-Design

**Justified Complexity**:
- 4 external dependencies (FastAPI, SQLAlchemy, Pydantic, pytest) - all standard choices
- 6 ORM models mapping to 6 database tables - matches 1:1 with schema
- 50+ API endpoints - required by spec (CRUD for 4 resources + reference data)

**Avoided Complexity**:
- ✅ No custom ORM or query builder
- ✅ No custom validation framework
- ✅ No background job processing
- ✅ No caching layer
- ✅ No API versioning (single version)
- ✅ No transfer transaction support (deferred to future)
- ✅ No transaction splits (deferred to future)

**Final Verdict**: Design adheres to all constitution principles. Ready for Phase 2 (Task Generation).
