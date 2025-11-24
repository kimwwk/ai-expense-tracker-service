# Tasks: Database Schema Discovery API

**Input**: Design documents from `/specs/002-database-schema-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Tests are included based on the plan.md test strategy (unit, integration, contract tests)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This project uses a single backend structure:
- **Source code**: `src/` at repository root
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project environment and dependencies

- [x] T001 Verify Python 3.11+ environment and existing dependencies (FastAPI, SQLAlchemy, Pydantic, psycopg2)
- [x] T002 Verify database connection to PostgreSQL with test query
- [x] T003 Review existing project structure (src/routers/, src/services/, src/schemas/)

**Checkpoint**: Environment verified - ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create Pydantic models and shared utilities needed by ALL user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create ColumnDefinition model in src/schemas/schema.py
- [x] T005 [P] Create ConstraintDefinition model in src/schemas/schema.py
- [x] T006 [P] Create TableSchema model in src/schemas/schema.py
- [x] T007 [P] Create DatabaseSchema model in src/schemas/schema.py
- [x] T008 [P] Create TableRelationship model in src/schemas/schema.py
- [x] T009 [P] Create ReferenceDataResponse model in src/schemas/schema.py
- [x] T010 Create APIRouter with prefix /schema in src/routers/schema.py
- [x] T011 Add logging configuration for schema operations in src/routers/schema.py

**Checkpoint**: Foundation ready - all Pydantic models defined, router initialized. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Explore Complete Database Structure (Priority: P1) 🎯 MVP

**Goal**: Enable developers and AI agents to discover the complete database schema in a single API call

**Independent Test**: Make GET /schema request and verify all tables, columns, constraints, and relationships are returned in structured format

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Create test fixture for database with known schema in tests/integration/test_schema_api.py
- [ ] T013 [P] [US1] Write integration test for GET /schema endpoint success case in tests/integration/test_schema_api.py
- [ ] T014 [P] [US1] Write integration test for GET /schema with multiple tables in tests/integration/test_schema_api.py
- [ ] T015 [P] [US1] Write integration test for GET /schema with relationships in tests/integration/test_schema_api.py
- [ ] T016 [P] [US1] Write integration test for GET /schema database error handling in tests/integration/test_schema_api.py
- [ ] T017 [P] [US1] Write unit test for get_all_tables service function in tests/unit/test_schema_service.py
- [ ] T018 [P] [US1] Write unit test for get_table_columns service function in tests/unit/test_schema_service.py
- [ ] T019 [P] [US1] Write unit test for get_table_constraints service function in tests/unit/test_schema_service.py
- [ ] T020 [P] [US1] Write unit test for extract_relationships service function in tests/unit/test_schema_service.py

### Implementation for User Story 1

- [ ] T021 [P] [US1] Implement get_all_tables function in src/services/schema_service.py (query information_schema.tables WHERE table_schema='public')
- [ ] T022 [P] [US1] Implement get_table_columns function in src/services/schema_service.py (query information_schema.columns with all metadata)
- [ ] T023 [P] [US1] Implement get_table_constraints function in src/services/schema_service.py (query table_constraints with key_column_usage joins)
- [ ] T024 [P] [US1] Implement extract_relationships function in src/services/schema_service.py (extract foreign keys from constraints)
- [ ] T025 [US1] Implement get_complete_schema function in src/services/schema_service.py (orchestrate all queries, return DatabaseSchema)
- [ ] T026 [US1] Implement GET /schema endpoint in src/routers/schema.py (call get_complete_schema, handle errors, add docstring)
- [ ] T027 [US1] Add error handling for database connection failures in src/routers/schema.py
- [ ] T028 [US1] Add logging for schema retrieval operations in src/routers/schema.py
- [ ] T029 [US1] Register schema router in src/main.py with app.include_router(schema.router)
- [ ] T030 [US1] Run all US1 tests to verify implementation: pytest tests/integration/test_schema_api.py::test_get_complete_schema -v
- [ ] T031 [US1] Manual test: curl http://localhost:8000/schema | jq . and verify response structure

**Checkpoint**: User Story 1 complete - GET /schema endpoint fully functional and testable independently. This is the MVP!

---

## Phase 4: User Story 2 - Inspect Individual Table Details (Priority: P2)

**Goal**: Enable focused inspection of specific table schema without fetching entire database schema

**Independent Test**: Request GET /schema/tables/accounts and verify column details, constraints, and foreign keys are returned. Test 404 for non-existent table.

### Tests for User Story 2

- [ ] T032 [P] [US2] Write integration test for GET /schema/tables/{table_name} success case in tests/integration/test_schema_api.py
- [ ] T033 [P] [US2] Write integration test for GET /schema/tables/{table_name} with foreign keys in tests/integration/test_schema_api.py
- [ ] T034 [P] [US2] Write integration test for GET /schema/tables/{table_name} 404 error in tests/integration/test_schema_api.py
- [ ] T035 [P] [US2] Write unit test for get_table_schema service function in tests/unit/test_schema_service.py

### Implementation for User Story 2

- [ ] T036 [US2] Implement get_table_schema function in src/services/schema_service.py (check table exists, reuse get_table_columns and get_table_constraints)
- [ ] T037 [US2] Implement GET /schema/tables/{table_name} endpoint in src/routers/schema.py (call get_table_schema, return 404 if not found)
- [ ] T038 [US2] Add validation for table_name parameter in src/routers/schema.py
- [ ] T039 [US2] Add logging for individual table schema requests in src/routers/schema.py
- [ ] T040 [US2] Run all US2 tests to verify implementation: pytest tests/integration/test_schema_api.py::test_get_table_schema -v
- [ ] T041 [US2] Manual test: curl http://localhost:8000/schema/tables/accounts | jq . and verify response
- [ ] T042 [US2] Manual test: curl http://localhost:8000/schema/tables/nonexistent and verify 404 response

**Checkpoint**: User Story 2 complete - GET /schema/tables/{name} endpoint fully functional and testable independently

---

## Phase 5: User Story 3 - Discover Table Relationships (Priority: P2)

**Goal**: Provide focused view of all foreign key relationships across the database for JOIN query construction

**Independent Test**: Request GET /schema/relationships and verify all foreign key relationships are returned with from_table, to_table, columns, and constraint names

### Tests for User Story 3

- [ ] T043 [P] [US3] Write integration test for GET /schema/relationships success case in tests/integration/test_schema_api.py
- [ ] T044 [P] [US3] Write integration test for GET /schema/relationships with multiple relationships in tests/integration/test_schema_api.py
- [ ] T045 [P] [US3] Write unit test for get_table_relationships service function in tests/unit/test_schema_service.py

### Implementation for User Story 3

- [ ] T046 [US3] Implement get_table_relationships function in src/services/schema_service.py (query information_schema for foreign keys only)
- [ ] T047 [US3] Implement GET /schema/relationships endpoint in src/routers/schema.py (call get_table_relationships, return list)
- [ ] T048 [US3] Add logging for relationships requests in src/routers/schema.py
- [ ] T049 [US3] Run all US3 tests to verify implementation: pytest tests/integration/test_schema_api.py::test_get_relationships -v
- [ ] T050 [US3] Manual test: curl http://localhost:8000/schema/relationships | jq . and verify response

**Checkpoint**: User Story 3 complete - GET /schema/relationships endpoint fully functional and testable independently

---

## Phase 6: User Story 4 - Access Reference Data Values (Priority: P3)

**Goal**: Provide quick access to reference table data for validation and UI population

**Independent Test**: Request GET /schema/reference-data?type=currencies and verify active currency records are returned. Test type=all returns all reference types.

### Tests for User Story 4

- [ ] T051 [P] [US4] Write integration test for GET /schema/reference-data?type=currencies in tests/integration/test_schema_api.py
- [ ] T052 [P] [US4] Write integration test for GET /schema/reference-data?type=account_types in tests/integration/test_schema_api.py
- [ ] T053 [P] [US4] Write integration test for GET /schema/reference-data?type=categories in tests/integration/test_schema_api.py
- [ ] T054 [P] [US4] Write integration test for GET /schema/reference-data?type=all in tests/integration/test_schema_api.py
- [ ] T055 [P] [US4] Write integration test for GET /schema/reference-data invalid type 422 error in tests/integration/test_schema_api.py
- [ ] T056 [P] [US4] Write unit test for get_reference_data service function in tests/unit/test_schema_service.py

### Implementation for User Story 4

- [ ] T057 [P] [US4] Implement get_currencies function in src/services/schema_service.py (query currencies WHERE is_active=TRUE)
- [ ] T058 [P] [US4] Implement get_account_types function in src/services/schema_service.py (query account_types)
- [ ] T059 [P] [US4] Implement get_categories function in src/services/schema_service.py (query categories WHERE is_active=TRUE)
- [ ] T060 [US4] Implement get_reference_data function in src/services/schema_service.py (orchestrate queries based on type parameter)
- [ ] T061 [US4] Implement GET /schema/reference-data endpoint in src/routers/schema.py (validate type param, call get_reference_data)
- [ ] T062 [US4] Add query parameter validation for type (enum: currencies, account_types, categories, all) in src/routers/schema.py
- [ ] T063 [US4] Add 422 error handling for invalid type parameter in src/routers/schema.py
- [ ] T064 [US4] Add logging for reference data requests in src/routers/schema.py
- [ ] T065 [US4] Run all US4 tests to verify implementation: pytest tests/integration/test_schema_api.py::test_get_reference_data -v
- [ ] T066 [US4] Manual test: curl 'http://localhost:8000/schema/reference-data?type=currencies' | jq . and verify response
- [ ] T067 [US4] Manual test: curl 'http://localhost:8000/schema/reference-data?type=all' | jq 'keys' and verify all types returned
- [ ] T068 [US4] Manual test: curl 'http://localhost:8000/schema/reference-data?type=invalid' and verify 422 error

**Checkpoint**: User Story 4 complete - GET /schema/reference-data endpoint fully functional and testable independently

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T069 [P] Verify all endpoints appear in OpenAPI docs at http://localhost:8000/docs
- [ ] T070 [P] Add comprehensive docstrings to all service functions in src/services/schema_service.py
- [ ] T071 [P] Add comprehensive docstrings to all router endpoints in src/routers/schema.py
- [ ] T072 [P] Review error handling consistency across all endpoints in src/routers/schema.py
- [ ] T073 [P] Review logging consistency across all endpoints in src/routers/schema.py
- [ ] T074 Run full test suite: pytest tests/ -v --cov=src/services/schema_service --cov=src/routers/schema --cov-report=term-missing
- [ ] T075 Measure performance: time curl http://localhost:8000/schema (should be <2s)
- [ ] T076 Measure performance: time curl http://localhost:8000/schema/tables/accounts (should be <200ms)
- [ ] T077 Measure performance: time curl 'http://localhost:8000/schema/reference-data?type=all' (should be <500ms)
- [ ] T078 [P] Review code for SQL injection vulnerabilities (all queries use parameterized statements)
- [ ] T079 [P] Verify only public schema tables are exposed (no pg_catalog or information_schema)
- [ ] T080 Follow quickstart.md verification steps for all phases
- [ ] T081 Update main API documentation with new /schema endpoints
- [ ] T082 Run final integration test suite against complete feature: pytest tests/integration/test_schema_api.py -v

**Checkpoint**: All user stories complete, polished, and validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Reuses US1 service functions but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Can reuse US1 relationship extraction but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Service functions before router endpoints
- Core implementation before error handling/logging
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: All 3 tasks can run in parallel if assigned to different people
- Phase 2: Tasks T004-T009 (all Pydantic models) can run in parallel (different classes in same file)
- User Story 1 tests: Tasks T012-T020 can all run in parallel (different test functions)
- User Story 1 implementation: Tasks T021-T024 can run in parallel (different service functions)
- User Story 2 tests: Tasks T032-T035 can run in parallel
- User Story 3 tests: Tasks T043-T045 can run in parallel
- User Story 4 tests: Tasks T051-T056 can run in parallel
- User Story 4 implementation: Tasks T057-T059 can run in parallel (different query functions)
- Phase 7: Tasks T069-T073, T078-T079 can run in parallel (different review areas)
- **MOST IMPORTANT**: After Phase 2 completes, User Stories 1, 2, 3, and 4 can ALL run in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (9 tests can run in parallel):
Task T012: "Create test fixture for database with known schema"
Task T013: "Write integration test for GET /schema endpoint success case"
Task T014: "Write integration test for GET /schema with multiple tables"
Task T015: "Write integration test for GET /schema with relationships"
Task T016: "Write integration test for GET /schema database error handling"
Task T017: "Write unit test for get_all_tables service function"
Task T018: "Write unit test for get_table_columns service function"
Task T019: "Write unit test for get_table_constraints service function"
Task T020: "Write unit test for extract_relationships service function"

# After tests are written and failing, launch service functions in parallel (4 functions):
Task T021: "Implement get_all_tables function"
Task T022: "Implement get_table_columns function"
Task T023: "Implement get_table_constraints function"
Task T024: "Implement extract_relationships function"
```

---

## Parallel Example: All User Stories After Foundational

```bash
# After Phase 2 (Foundational) completes, these can run in parallel:
Developer A: Works on User Story 1 (Tasks T012-T031) - Complete database schema
Developer B: Works on User Story 2 (Tasks T032-T042) - Individual table details
Developer C: Works on User Story 3 (Tasks T043-T050) - Table relationships
Developer D: Works on User Story 4 (Tasks T051-T068) - Reference data

# Each developer completes their story independently and tests it without blocking others
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011) - **CRITICAL GATE**
3. Complete Phase 3: User Story 1 (T012-T031)
4. **STOP and VALIDATE**: Test User Story 1 independently with quickstart.md verification
5. Deploy/demo GET /schema endpoint as MVP

**MVP Deliverable**: Developers and AI agents can discover complete database schema in a single API call

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! Complete schema discovery)
3. Add User Story 2 → Test independently → Deploy/Demo (Add focused table inspection)
4. Add User Story 3 → Test independently → Deploy/Demo (Add relationship graph)
5. Add User Story 4 → Test independently → Deploy/Demo (Add reference data access)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With 4 developers:

1. **Together**: Complete Setup + Foundational (Phase 1-2)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (Complete schema)
   - Developer B: User Story 2 (Table details)
   - Developer C: User Story 3 (Relationships)
   - Developer D: User Story 4 (Reference data)
3. Stories complete and integrate independently
4. **Together**: Polish phase (final validation)

---

## Task Summary

**Total Tasks**: 82 tasks

### Tasks by User Story
- **Setup**: 3 tasks
- **Foundational**: 8 tasks (BLOCKS all stories)
- **User Story 1 (P1)**: 20 tasks (9 tests + 11 implementation)
- **User Story 2 (P2)**: 11 tasks (4 tests + 7 implementation)
- **User Story 3 (P2)**: 8 tasks (3 tests + 5 implementation)
- **User Story 4 (P3)**: 18 tasks (6 tests + 12 implementation)
- **Polish**: 14 tasks

### Parallel Opportunities Identified
- **41 tasks** marked with [P] can run in parallel within their phase
- **4 user stories** can run completely in parallel after Foundational phase
- **MVP scope**: User Story 1 only = 31 tasks (Setup + Foundational + US1)

### Independent Test Criteria
- **US1**: Single API call returns all tables, columns, constraints, relationships
- **US2**: Request specific table schema, verify details returned, 404 for invalid table
- **US3**: Request relationships, verify foreign key graph is complete
- **US4**: Request reference data by type, verify active records only, test type=all

### Suggested MVP Scope

**Minimum Viable Product = User Story 1 (Complete Database Schema)**
- Tasks: T001-T031 (31 tasks)
- Deliverable: GET /schema endpoint
- Value: Developers and AI agents can discover entire database structure
- Estimated effort: 1-2 days for experienced developer
- Testing: Comprehensive (9 tests for schema accuracy)

After MVP proves valuable, add User Stories 2-4 incrementally based on user feedback.

---

## Notes

- [P] tasks = different files/functions, no dependencies, can run in parallel
- [Story] label (US1, US2, US3, US4) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All SQL queries use parameterized statements for security
- Only public schema tables exposed
- Performance targets: <200ms single table, <2s complete schema, <500ms reference data
