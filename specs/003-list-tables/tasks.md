# Tasks: Table Names List Endpoint

**Feature**: 003-list-tables
**Branch**: `003-list-tables`
**Created**: 2025-11-24

**Total Tasks**: 23 tasks
**Estimated Time**: 30-60 minutes (simple feature extending existing patterns)

## Overview

This task list implements a lightweight endpoint that returns all table names from the public schema. This is a simple feature with only one user story (P1) that extends the existing schema discovery API (feature 002).

## Task Organization

Tasks are organized into phases:

1. **Phase 1**: Setup (verify environment - 3 tasks)
2. **Phase 2**: User Story 1 - Quick Table Discovery (17 tasks)
3. **Phase 3**: Polish & Validation (3 tasks)

## Phase 1: Setup & Prerequisites

**Goal**: Verify environment is ready for implementation

- [x] T001 Verify Python 3.11 environment is active with `.venv/bin/python --version`
- [x] T002 Verify existing schema router and service files exist: `src/routers/schema.py` and `src/services/schema_service.py`
- [x] T003 Verify database connection with test query: `psql` or `.venv/bin/python -c "from src.database import get_db; next(get_db())"`

**Checkpoint**: Environment verified, existing files confirmed

---

## Phase 2: User Story 1 - Quick Table Discovery (P1)

**Story Goal**: Implement GET /schema/tables endpoint that returns a simple list of all table names from the public schema.

**Why P1**: This is the core (and only) requirement for this feature - a lightweight table discovery endpoint.

**Independent Test**: Make a GET request to /schema/tables and verify it returns an alphabetically sorted array of table names from the public schema.

### Service Layer Implementation

- [x] T004 [P] [US1] Read existing `src/services/schema_service.py` to understand patterns
- [x] T005 [US1] Add `get_table_names(db: Session) -> List[str]` function to `src/services/schema_service.py`
- [x] T006 [US1] Implement SQL query using `text()`: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name
- [x] T007 [US1] Extract table names using list comprehension: `[row.table_name for row in result]`
- [x] T008 [US1] Add logging statement: `logger.info(f"Retrieved {len(table_names)} table names")` in `src/services/schema_service.py`

**Checkpoint**: Service function returns list of table names

### Router Endpoint Implementation

- [x] T009 [P] [US1] Read existing `src/routers/schema.py` to understand endpoint patterns
- [x] T010 [US1] Import `List` from typing if not already imported in `src/routers/schema.py`
- [x] T011 [US1] Add `@router.get("/tables", response_model=List[str], summary="Get all table names")` endpoint to `src/routers/schema.py`
- [x] T012 [US1] Implement `get_table_names_endpoint(db: Session = Depends(get_db))` function in `src/routers/schema.py`
- [x] T013 [US1] Call `schema_service.get_table_names(db)` from endpoint in `src/routers/schema.py`
- [x] T014 [US1] Add try/except block for SQLAlchemyError with HTTP 500 response in `src/routers/schema.py`
- [x] T015 [US1] Add logging for requests and errors in endpoint function in `src/routers/schema.py`
- [x] T016 [US1] Return table_names list from endpoint in `src/routers/schema.py`

**Checkpoint**: Endpoint implemented and router updated

### Testing & Verification

- [ ] T017 [P] [US1] Start development server: `uvicorn src.main:app --reload` (or use existing server)
- [ ] T018 [US1] Test endpoint with curl: `curl http://localhost:8000/schema/tables` and verify response is JSON array
- [ ] T019 [US1] Verify response contains expected table names (accounts, transactions, categories, etc.)
- [ ] T020 [US1] Verify response is alphabetically sorted
- [ ] T021 [US1] Test with browser at http://localhost:8000/docs and execute /schema/tables endpoint

**Checkpoint**: User Story 1 complete - endpoint returns table names successfully

---

## Phase 3: Polish & Final Validation

**Purpose**: Final checks and documentation

- [ ] T022 Verify endpoint appears in OpenAPI docs at http://localhost:8000/docs with proper summary and description
- [ ] T023 Measure performance: `time curl http://localhost:8000/schema/tables` should be <100ms

**Checkpoint**: Feature complete and validated

---

## Dependencies & Execution Order

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies (extends existing schema API)

### Task Dependencies

**Sequential Blocks**:

1. Setup (T001-T003) → MUST complete first
2. Service Layer (T004-T008) → BLOCKS Router Implementation
3. Router Implementation (T009-T016) → BLOCKS Testing
4. Testing (T017-T021) → BLOCKS Polish
5. Polish (T022-T023) → Final phase

### Parallel Opportunities

Tasks marked [P] can run in parallel within their phase:

**Phase 1 Setup**:
- T001, T002, T003 can run in parallel (independent checks)

**Phase 2 User Story 1**:
- T004 (read service) and T009 (read router) can run in parallel (different files)
- T017 (start server) can overlap with T018-T021 (testing)
- T022-T023 (polish) can run in parallel (different verification tasks)

**Parallelization Example**:
```
Developer workflow:
1. Run T001-T003 simultaneously (3 terminal windows)
2. Run T004 and T009 simultaneously (read both files at once)
3. Implement T005-T008 (service layer)
4. Implement T010-T016 (router layer)
5. T017 start server, then T018-T021 test in parallel
6. T022-T023 verify in parallel
```

---

## Implementation Strategy

### MVP Scope

**Minimum Viable Product = User Story 1** (all 23 tasks)

This feature has only one user story, so the MVP is the complete feature:
- Service function to query table names
- Router endpoint GET /schema/tables
- Basic testing and validation

**Deliverable**: Working endpoint that returns table names in <100ms

**Time Estimate**: 30-60 minutes

### Incremental Delivery

Since this is a single user story feature, delivery is straightforward:

1. **Commit 1**: Service layer implementation (T004-T008)
2. **Commit 2**: Router endpoint implementation (T010-T016)
3. **Commit 3**: Testing and polish (T017-T023)

Each commit is a working increment that can be tested independently.

---

## Testing Strategy

### Manual Testing Checklist

After completing Phase 2:

- [ ] GET /schema/tables returns 200 status
- [ ] Response is valid JSON array of strings
- [ ] Response contains expected tables: ["account_types", "accounts", "categories", "currencies", "payees", "transactions", ...]
- [ ] Response is alphabetically sorted
- [ ] Response time is <100ms
- [ ] No system tables (pg_catalog, information_schema) in response
- [ ] Endpoint appears in /docs with proper documentation

### Test Examples

**curl test**:
```bash
curl -i http://localhost:8000/schema/tables
```

**Expected response**:
```json
[
  "account_types",
  "accounts",
  "categories",
  "currencies",
  "payees",
  "transactions",
  "transaction_splits",
  "users"
]
```

**Performance test**:
```bash
time curl -s http://localhost:8000/schema/tables > /dev/null
# Should complete in <100ms
```

---

## Task Summary

**Total Tasks**: 23 tasks

### Tasks by Phase
- **Setup**: 3 tasks
- **User Story 1 (P1)**: 17 tasks
  - Service layer: 5 tasks
  - Router layer: 8 tasks
  - Testing: 4 tasks
- **Polish**: 3 tasks

### Parallel Opportunities
- **6 tasks** marked with [P] can run in parallel with other tasks in their phase
- Service layer and router reading (T004, T009) can overlap
- Testing tasks (T018-T021) can run concurrently
- Polish tasks (T022-T023) can run in parallel

### MVP Scope
**All 23 tasks = MVP** (single user story feature)

Time estimate: 30-60 minutes for experienced developer

---

## Notes

- **Simple Feature**: This is a straightforward extension of existing schema API
- **Pattern Matching**: Follow existing patterns from `src/routers/schema.py` and `src/services/schema_service.py`
- **No New Dependencies**: Uses existing FastAPI, SQLAlchemy, Pydantic stack
- **No Schema Changes**: Read-only query to information_schema
- **Performance Target**: <100ms (much simpler than existing schema endpoints)
- **Quick Win**: High value, low complexity feature for developers and AI agents

**Verification**: After T023, feature is complete and ready for commit/PR.
