# Implementation Plan: Database Schema Discovery API

**Branch**: `002-database-schema-api` | **Date**: 2025-11-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-database-schema-api/spec.md`

## Summary

This feature adds a new REST API controller that exposes database schema information to developers and AI agents. The API will provide endpoints to retrieve complete database schema (all tables, columns, constraints, relationships), inspect individual table details, discover foreign key relationships, and access reference data values. The implementation queries PostgreSQL's `information_schema` views to dynamically reflect the current database structure without hardcoding schema definitions.

**Primary Value**: Enables developers and AI agents to discover and understand the database structure programmatically, facilitating query construction, data validation, and automated tooling integration.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI 0.104+, SQLAlchemy 2.0+, Pydantic 2.5+, psycopg2-binary 2.9+
**Storage**: PostgreSQL (querying information_schema views)
**Testing**: pytest 7.4+, pytest-asyncio 0.21+, httpx 0.25+
**Target Platform**: Linux server (containerized deployment)
**Project Type**: Single backend service (REST API)
**Performance Goals**: <200ms p95 latency for single table queries, <2s for complete schema retrieval (up to 50 tables)
**Constraints**: Sub-500ms for reference data queries, response sizes up to 5MB for large schemas
**Scale/Scope**: Database with ~15-20 application tables, 3-4 reference tables, 20-30 foreign key relationships

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md` principles:

### Code Quality & Simplicity
- [x] Each component has single, clear responsibility
  - Router handles HTTP concerns only
  - Service layer handles database schema queries
  - Pydantic schemas handle response serialization
- [x] No premature abstractions planned
  - Following existing project patterns (router → service → database)
  - No new abstraction layers needed
- [x] Design choices favor boring, obvious solutions over clever ones
  - Standard FastAPI endpoint patterns
  - Direct SQL queries to information_schema (PostgreSQL standard)
  - Straightforward JSON response structures
- [x] Implementation complexity justified if unavoidable
  - SQL queries may be moderately complex due to information_schema joins, but this is inherent to the problem domain

### Testing Standards
- [x] Test strategy defined (unit, integration, contract)
  - Unit tests: Service layer functions (schema parsing, query construction)
  - Integration tests: End-to-end API endpoint tests with test database
  - Contract tests: OpenAPI schema validation for response formats
- [x] Tests can be written alongside or before implementation
  - Service layer queries can be tested immediately with test database
  - API contracts can be validated against OpenAPI spec
- [x] Test isolation and independence verified
  - Each test uses database fixtures with known schema state
  - No cross-test dependencies
- [x] Critical business logic test coverage planned
  - Schema retrieval accuracy (all tables, columns, constraints returned)
  - Filtering logic (public schema only, active records only)
  - Error handling (non-existent tables, connection failures)

### User Experience Consistency
- [x] Loading states defined for async operations >200ms
  - Not applicable: This is a backend API (no UI loading states)
  - API returns standard HTTP status codes for async operations
- [x] Error handling provides clear, actionable feedback
  - 404 for non-existent tables with clear message
  - 500 for database connection errors with error details
  - 422 for invalid reference data type requests with valid options listed
- [x] Mobile-first responsive design approach
  - Not applicable: This is a backend API
- [x] Accessibility requirements (WCAG 2.1 AA) planned
  - Not applicable: This is a backend API

### Performance Requirements
- [x] API latency targets defined (<200ms p95 simple, <1s complex)
  - Single table schema: <200ms p95
  - Complete database schema: <2s for 50 tables
  - Reference data: <500ms
- [x] Resource constraints documented (<500MB backend, <2MB frontend bundle)
  - Response size limits: <5MB for large schemas
  - Memory: Fits within existing service constraints (<500MB per instance)
  - No frontend bundle impact (backend-only feature)
- [x] Monitoring and metrics strategy defined
  - Endpoint latency metrics (via existing FastAPI middleware)
  - Error rate monitoring (via logging)
  - Response size tracking for schema endpoints
- [x] Performance budgets established
  - Query execution time: <1s for complex schema queries
  - Response serialization: <200ms for large result sets

### Complexity Justification
If any of the following apply, document justification:
- New external dependencies: None (uses existing FastAPI, SQLAlchemy, psycopg2)
- New abstraction layers: None (follows existing router → service pattern)
- Performance optimizations sacrificing readability: None planned (queries are standard SQL)
- Architecture changes affecting multiple modules: None (isolated schema router)

**No complexity justification required** - this feature follows existing patterns and introduces no new abstractions or dependencies.

## Project Structure

### Documentation (this feature)

```text
specs/002-database-schema-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── openapi.yaml     # OpenAPI spec for schema endpoints
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/              # Existing SQLAlchemy models (no changes needed)
├── schemas/             # Pydantic response schemas
│   └── schema.py        # NEW: Schema discovery response models
├── services/            # Business logic layer
│   └── schema_service.py # NEW: Database schema query logic
└── routers/             # FastAPI route handlers
    └── schema.py        # NEW: Schema discovery endpoints

tests/
├── integration/
│   └── test_schema_api.py # NEW: End-to-end API tests
└── unit/
    └── test_schema_service.py # NEW: Service layer unit tests
```

**Structure Decision**: This project uses a single backend structure with clear separation of concerns:
- **routers/**: HTTP endpoint definitions (FastAPI routers)
- **services/**: Business logic and database queries
- **schemas/**: Request/response models (Pydantic)
- **models/**: ORM models (SQLAlchemy) - not needed for this feature as we query information_schema directly

The schema discovery feature adds one new module to each layer: `schema.py` router, `schema_service.py` service, and `schema.py` schemas.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - table is empty.

## Post-Design Constitution Re-Evaluation

*Completed after Phase 1 design artifacts generated*

### Code Quality & Simplicity - ✅ PASS

**Review**: Design maintains single responsibility principle throughout:
- Router layer: HTTP concerns only (endpoints, status codes, error responses)
- Service layer: Database queries to information_schema, result transformation
- Schema layer: Response serialization and validation

**No new abstractions introduced**. Pattern follows existing codebase conventions (accounts, transactions routers).

**SQL queries to information_schema are standard PostgreSQL** - no clever tricks, just joins on standard views.

**Justification for moderate SQL complexity**: Querying information_schema requires joins between `tables`, `columns`, and `constraints` views. This is inherent to the problem domain and cannot be simplified without losing functionality.

### Testing Standards - ✅ PASS

**Test strategy confirmed**:
- Unit tests: Service layer functions return correct data structures
- Integration tests: End-to-end API tests with test database
- Contract tests: OpenAPI validation (FastAPI generates from Pydantic models)

**Tests can be written alongside implementation** - service functions testable immediately with database fixtures.

**Critical business logic coverage**:
- Schema accuracy (all tables, columns, constraints returned)
- Filtering (public schema only)
- Error handling (404, 422, 500 cases)
- Reference data filtering (active records only)

### User Experience Consistency - ✅ PASS

**Error responses follow existing project format**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Clear, actionable message",
    "details": { "context": "values" }
  }
}
```

**HTTP status codes match conventions**:
- 200: Success
- 404: Table not found
- 422: Invalid parameter
- 500: Database error

### Performance Requirements - ✅ PASS

**Targets defined and achievable**:
- Single table: <200ms (simple query with parameterized table name)
- Complete schema: <2s for 50 tables (loop with N queries, still fast)
- Reference data: <500ms (small tables, filtered queries)

**No performance optimizations sacrificing readability** - queries are straightforward SQL.

**Monitoring strategy**: Existing FastAPI middleware captures endpoint latency. Logging added for errors.

### Final Assessment

**All Constitution principles satisfied**. No compromises or violations. Design is boring, testable, and follows existing patterns.

**Ready to proceed to implementation** (`/speckit.tasks` to generate task breakdown).

## Phase 0: Research Summary

Documented in [research.md](./research.md).

**Key Decisions**:
1. Use PostgreSQL information_schema views (standard SQL approach)
2. RESTful endpoint design with 4 focused endpoints
3. Structured JSON responses matching information_schema field names
4. Existing project error response format
5. No pagination for MVP (schemas are small, can add later if needed)

**All technical unknowns resolved**. No open questions remaining.

## Phase 1: Design Artifacts

### Generated Artifacts

1. **[data-model.md](./data-model.md)** - Pydantic response models
   - `ColumnDefinition`: Column metadata
   - `ConstraintDefinition`: Constraint metadata
   - `TableSchema`: Single table structure
   - `DatabaseSchema`: Complete schema
   - `TableRelationship`: Foreign key relationships
   - `ReferenceDataResponse`: Reference data wrapper

2. **[contracts/openapi.yaml](./contracts/openapi.yaml)** - OpenAPI 3.1 specification
   - 4 endpoint definitions with examples
   - Complete schema definitions
   - Error response formats
   - Query parameter validation

3. **[quickstart.md](./quickstart.md)** - Implementation guide
   - Phase-by-phase checklist
   - Quick start commands
   - Testing examples
   - Troubleshooting guide

### Implementation Sequence

Based on user story priorities from spec:

1. **Phase 1 (P1)**: `GET /schema` - Complete database schema
2. **Phase 2 (P2)**: `GET /schema/tables/{name}` + `GET /schema/relationships`
3. **Phase 3 (P3)**: `GET /schema/reference-data?type={type}`

Each phase is independently testable and delivers standalone value.

## Next Steps

1. **Run `/speckit.tasks`** to generate detailed implementation task breakdown
2. **Implement Phase 1** following quickstart.md checklist
3. **Test thoroughly** at each phase before proceeding to next
4. **Commit incrementally** after each working phase

## References

- Feature Specification: [spec.md](./spec.md)
- Technical Research: [research.md](./research.md)
- Data Models: [data-model.md](./data-model.md)
- API Contracts: [contracts/openapi.yaml](./contracts/openapi.yaml)
- Implementation Guide: [quickstart.md](./quickstart.md)
- Project Constitution: `.specify/memory/constitution.md`
