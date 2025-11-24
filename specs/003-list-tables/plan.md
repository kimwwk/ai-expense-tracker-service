# Implementation Plan: Table Names List Endpoint

**Branch**: `003-list-tables` | **Date**: 2025-11-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-list-tables/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a lightweight endpoint to the existing schema router that returns a simple list of all table names from the public schema. This extends the schema discovery API (feature 002) with a minimal overhead operation for quick table exploration.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI 0.121.2, SQLAlchemy 2.0.44, Pydantic 2.5+
**Storage**: PostgreSQL (querying information_schema.tables)
**Testing**: pytest with TestClient for endpoint testing
**Target Platform**: Linux server (existing deployment)
**Project Type**: Single backend service (extending existing)
**Performance Goals**: <100ms response time for table list retrieval
**Constraints**: Public schema tables only, alphabetically sorted, no views
**Scale/Scope**: Minimal - single new endpoint in existing router

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md` principles:

### Code Quality & Simplicity
- [x] Each component has single, clear responsibility
  - New service function: get table names only
  - New router endpoint: expose table names via REST
- [x] No premature abstractions planned
  - Reuses existing schema_service.py and schema router patterns
- [x] Design choices favor boring, obvious solutions over clever ones
  - Simple SQL query to information_schema.tables
  - Return List[str] - no complex data structures
- [x] Implementation complexity justified if unavoidable
  - No complexity - straightforward query and response

### Testing Standards
- [x] Test strategy defined (unit, integration, contract)
  - Unit: Test service function returns correct table names
  - Integration: Test endpoint with TestClient
  - Contract: Verify OpenAPI schema matches response
- [x] Tests can be written alongside or before implementation
  - Yes - clear expected behavior (list of table names)
- [x] Test isolation and independence verified
  - Tests use existing database session fixtures
- [x] Critical business logic test coverage planned
  - Verify only public schema tables returned
  - Verify alphabetical sorting
  - Verify empty array when no tables

### User Experience Consistency
- [x] Loading states defined for async operations >200ms
  - Target is <100ms, no loading state needed
- [x] Error handling provides clear, actionable feedback
  - Follows existing schema endpoint error patterns
  - 500 errors for database failures with clear messages
- [x] Mobile-first responsive design approach
  - N/A (API endpoint only)
- [x] Accessibility requirements (WCAG 2.1 AA) planned
  - N/A (API endpoint only)

### Performance Requirements
- [x] API latency targets defined (<200ms p95 simple, <1s complex)
  - Target: <100ms (simpler than existing schema endpoints)
- [x] Resource constraints documented (<500MB backend, <2MB frontend bundle)
  - Minimal memory impact (simple string array)
- [x] Monitoring and metrics strategy defined
  - Uses existing logging infrastructure
- [x] Performance budgets established
  - <100ms target, query is simple (no joins, minimal columns)

### Complexity Justification
No violations - this feature:
- Uses existing dependencies (no new packages)
- Follows established patterns from feature 002
- No new abstraction layers
- No performance optimizations needed (query is inherently fast)
- Extends existing router (no architecture changes)

## Project Structure

### Documentation (this feature)

```text
specs/003-list-tables/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── openapi.yaml     # OpenAPI schema for new endpoint
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── routers/
│   └── schema.py           # MODIFY: Add new endpoint
├── services/
│   └── schema_service.py   # MODIFY: Add get_table_names function
└── schemas/
    └── schema.py           # NO CHANGE: List[str] is sufficient

tests/
├── unit/
│   └── test_schema_service.py  # NEW: Unit tests for get_table_names
└── integration/
    └── test_schema_api.py      # MODIFY: Add endpoint tests
```

**Structure Decision**: Single project structure. This feature extends existing schema discovery functionality (feature 002) by adding one new service function and one new router endpoint. No new modules or packages required.

## Complexity Tracking

No violations requiring justification. This feature follows existing patterns and introduces no new complexity.

## Planning Phase Complete

**Status**: ✅ All phases complete

### Artifacts Generated

1. **research.md**: Technical decisions documented
   - Query strategy (information_schema.tables)
   - Response format (List[str])
   - Service layer design
   - Router endpoint design
   - Testing strategy

2. **data-model.md**: Data model specification
   - Response type: List[str]
   - Database schema (read-only)
   - Type signatures
   - Error responses

3. **contracts/openapi.yaml**: OpenAPI specification
   - GET /schema/tables endpoint
   - Response schema (array of strings)
   - Error responses (500)
   - Examples and documentation

4. **quickstart.md**: Implementation guide
   - Step-by-step checklist (5 phases, 30-60 min)
   - Code templates (service, router, tests)
   - Testing examples (curl, Python)
   - Troubleshooting guide

5. **Agent context updated**: CLAUDE.md updated with feature details

### Constitution Verification (Post-Design)

✅ All constitution checks pass:
- Single responsibility maintained
- No premature abstractions
- Boring, obvious solution chosen
- Clear test strategy
- Performance targets defined (<100ms)
- No unjustified complexity

### Ready for Next Phase

**Next command**: `/speckit.tasks`

This will generate:
- Detailed task breakdown with IDs
- Test tasks for TDD approach
- Parallel execution opportunities
- MVP scope definition
