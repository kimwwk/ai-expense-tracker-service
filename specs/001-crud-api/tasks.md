# Tasks: Basic CRUD REST API for Expense Tracking

**Input**: Design documents from `/specs/001-crud-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are included per the testing strategy defined in plan.md (unit, integration, contract tests)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)
- All paths are absolute from repository root: `/home/user1/ai-expense-app-bundle/ai-expense-tracker-service/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (src/{models,schemas,routers,services}, tests/{unit,integration,contract})
- [X] T002 Create all __init__.py files in src/ and tests/ directories
- [X] T003 Create pyproject.toml with FastAPI, SQLAlchemy, Pydantic, psycopg2-binary, uvicorn dependencies
- [X] T004 Create .env.example with DATABASE_URL, ENVIRONMENT, LOG_LEVEL, DB_POOL_SIZE, DB_MAX_OVERFLOW
- [X] T005 [P] Create .gitignore for Python (.env, __pycache__, .pytest_cache, .venv, *.pyc)
- [X] T006 [P] Create README.md with project description, setup instructions, and API docs link

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Implement configuration management in src/config.py using pydantic-settings
- [X] T008 Implement database session management in src/database.py with SQLAlchemy engine and get_db dependency
- [X] T009 Create FastAPI application in src/main.py with CORS middleware and /health endpoint
- [X] T010 [P] Create common Pydantic schemas in src/schemas/common.py (PaginationMetadata, PaginatedResponse, ErrorResponse)
- [X] T011 [P] Create enums in src/schemas/enums.py (TransactionType, TransactionStatus, CategoryType)
- [X] T012 [P] Create pytest conftest.py in tests/conftest.py with db_session and client fixtures
- [X] T013 Verify database connection and health endpoint works (uvicorn src.main:app --reload)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 4 - Manage Accounts (Priority: P1) 🎯 MVP Foundation

**Goal**: Enable users to create and retrieve accounts (bank accounts, credit cards, cash) - required foundation for all transactions

**Independent Test**: Create an account with POST /accounts, retrieve it with GET /accounts/{id}, list all accounts with GET /accounts, verify account structure with current_balance

**Why First**: Accounts are a foreign key dependency for transactions. Must exist before any transactions can be created.

### Implementation for User Story 4

- [X] T014 [P] [US4] Create Currency model in src/models/currency.py mapping to currencies table
- [X] T015 [P] [US4] Create AccountType model in src/models/account_type.py mapping to account_types table
- [X] T016 [US4] Create Account model in src/models/account.py with relationships to AccountType and Currency
- [X] T017 [P] [US4] Create Currency response schema in src/schemas/currency.py (CurrencyResponse)
- [X] T018 [P] [US4] Create AccountType response schema in src/schemas/account_type.py (AccountTypeResponse)
- [X] T019 [US4] Create Account schemas in src/schemas/account.py (AccountCreate, AccountUpdate, AccountResponse)
- [X] T020 [US4] Implement account service CRUD functions in src/services/account_service.py (create, get, list with filters, update, delete)
- [X] T021 [US4] Implement account router in src/routers/accounts.py (POST, GET /{id}, GET list, PUT, PATCH, DELETE)
- [X] T022 [US4] Register accounts router in src/main.py with app.include_router
- [X] T023 [US4] Add error handling for foreign key violations and not found errors in account router
- [ ] T024 [P] [US4] Write unit tests for account service in tests/unit/test_account_service.py
- [X] T025 [US4] Write integration tests for account API in tests/integration/test_accounts_api.py

**Checkpoint**: At this point, accounts can be created, retrieved, listed, updated, and deleted. Current balance is visible (maintained by database triggers).

---

## Phase 4: User Story 6 - Access Reference Data (Priority: P3)

**Goal**: Provide read-only access to account types and currencies for UI dropdowns and data consistency

**Independent Test**: Send GET requests to /account-types and /currencies, verify standard reference data is returned

**Why Second**: Simple, no dependencies, provides supporting data for accounts and transactions

### Implementation for User Story 6

- [X] T026 [P] [US6] Implement reference service functions in src/services/reference_service.py (list_account_types, list_currencies)
- [X] T027 [US6] Implement reference router in src/routers/reference.py (GET /account-types, GET /currencies)
- [X] T028 [US6] Register reference router in src/main.py with app.include_router
- [X] T029 [US6] Write integration tests for reference API in tests/integration/test_reference_api.py

**Checkpoint**: Reference data endpoints functional. Account types and currencies can be retrieved.

---

## Phase 5: User Story 1 - Create and Retrieve Transaction (Priority: P1) 🎯 MVP Core

**Goal**: Enable users to record new transactions and retrieve them to verify details were saved

**Independent Test**: Send POST request with transaction data, receive 201 with created transaction and Location header, then GET by ID to retrieve the same transaction

**Dependencies**: Requires Phase 3 (Accounts) to be complete

### Implementation for User Story 1

- [X] T030 [P] [US1] Create Category model in src/models/category.py mapping to categories table
- [X] T031 [P] [US1] Create Payee model in src/models/payee.py mapping to payees table
- [X] T032 [US1] Create Transaction model in src/models/transaction.py with relationships to Account, Category, Payee, Currency
- [X] T033 [P] [US1] Create Category schemas in src/schemas/category.py (CategoryResponse for reference)
- [X] T034 [P] [US1] Create Payee schemas in src/schemas/payee.py (PayeeResponse for reference)
- [X] T035 [US1] Create Transaction schemas in src/schemas/transaction.py (TransactionCreate, TransactionResponse)
- [X] T036 [US1] Implement transaction service functions in src/services/transaction_service.py (create_transaction, get_transaction)
- [X] T037 [US1] Implement transaction router POST and GET/{id} endpoints in src/routers/transactions.py
- [X] T038 [US1] Register transactions router in src/main.py with app.include_router
- [X] T039 [US1] Add error handling for foreign key violations, not found errors, and validation errors in transaction router
- [ ] T040 [P] [US1] Write unit tests for create and get transaction in tests/unit/test_transaction_service.py
- [X] T041 [US1] Write integration tests for POST and GET transaction in tests/integration/test_transactions_api.py (create, retrieve, 404 error)

**Checkpoint**: At this point, transactions can be created and retrieved by ID. Account balances automatically update via database triggers. This is the core MVP functionality.

---

## Phase 6: User Story 2 - Update and Delete Transaction (Priority: P2)

**Goal**: Enable users to correct errors in transactions or remove mistaken entries

**Independent Test**: Create a transaction, send PATCH to modify fields, verify with GET, then DELETE and confirm 404 on subsequent GET

**Dependencies**: Requires Phase 5 (US1 - Create/Retrieve Transaction) to be complete

### Implementation for User Story 2

- [ ] T042 [US2] Add TransactionUpdate schema to src/schemas/transaction.py for partial updates
- [ ] T043 [US2] Implement update and delete functions in src/services/transaction_service.py (update_transaction, patch_transaction, delete_transaction)
- [ ] T044 [US2] Implement PUT, PATCH, and DELETE endpoints in src/routers/transactions.py
- [ ] T045 [US2] Add validation for update operations (ensure foreign keys exist, amounts positive, dates valid)
- [ ] T046 [P] [US2] Write unit tests for update and delete in tests/unit/test_transaction_service.py
- [ ] T047 [US2] Write integration tests for PUT, PATCH, DELETE in tests/integration/test_transactions_api.py

**Checkpoint**: Transactions can be fully updated (PUT), partially updated (PATCH), and deleted. Database triggers automatically adjust account balances.

---

## Phase 7: User Story 3 - List and Filter Transactions (Priority: P2)

**Goal**: Enable users to view and filter transactions by date range, account, category, status for expense analysis

**Independent Test**: Create multiple transactions with different attributes, send GET with various filters (account_id, date range, category_id), verify filtered results and pagination

**Dependencies**: Requires Phase 5 (US1) to be complete

### Implementation for User Story 3

- [ ] T048 [US3] Implement list_transactions function in src/services/transaction_service.py with filtering (account_id, category_id, payee_id, transaction_type, status, start_date, end_date) and pagination
- [ ] T049 [US3] Implement GET /transactions list endpoint in src/routers/transactions.py with all filter parameters
- [ ] T050 [US3] Add sorting support (sort, order parameters) to list endpoint
- [ ] T051 [US3] Implement pagination validation (limit max 100, default 50, offset default 0)
- [ ] T052 [P] [US3] Write unit tests for list and filter logic in tests/unit/test_transaction_service.py
- [ ] T053 [US3] Write integration tests for list, filter, pagination, sorting in tests/integration/test_transactions_api.py

**Checkpoint**: Transactions can be listed with pagination, filtered by multiple criteria, and sorted. Users can analyze spending patterns.

---

## Phase 8: User Story 5 - Manage Categories and Payees (Priority: P3)

**Goal**: Enable users to create and manage expense categories and payees for transaction classification

**Independent Test**: Create categories via POST, retrieve them via GET, create payees via POST, retrieve them, then associate with transactions

**Dependencies**: No blocking dependencies (transactions work without these, but enhanced when present)

### Implementation for User Story 5

- [ ] T054 [P] [US5] Complete Category schemas in src/schemas/category.py (CategoryCreate, CategoryUpdate, CategoryResponse)
- [ ] T055 [P] [US5] Complete Payee schemas in src/schemas/payee.py (PayeeCreate, PayeeUpdate, PayeeResponse)
- [ ] T056 [P] [US5] Implement category service in src/services/category_service.py (create, get, list with filters, update, delete)
- [ ] T057 [P] [US5] Implement payee service in src/services/payee_service.py (create, get, list with filters, update, delete)
- [ ] T058 [P] [US5] Implement category router in src/routers/categories.py (POST, GET/{id}, GET list, PUT, PATCH, DELETE)
- [ ] T059 [P] [US5] Implement payee router in src/routers/payees.py (POST, GET/{id}, GET list, PUT, PATCH, DELETE)
- [ ] T060 [P] [US5] Register categories and payees routers in src/main.py
- [ ] T061 [P] [US5] Write unit tests for category service in tests/unit/test_category_service.py
- [ ] T062 [P] [US5] Write unit tests for payee service in tests/unit/test_payee_service.py
- [ ] T063 [P] [US5] Write integration tests for categories API in tests/integration/test_categories_api.py
- [ ] T064 [P] [US5] Write integration tests for payees API in tests/integration/test_payees_api.py

**Checkpoint**: Categories and payees can be fully managed. Transactions can reference them for better organization and reporting.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final production readiness

- [ ] T065 [P] Write contract tests validating OpenAPI spec compliance in tests/contract/test_openapi_compliance.py
- [ ] T066 [P] Add comprehensive error handling examples to README.md
- [ ] T067 [P] Create Dockerfile for containerized deployment
- [ ] T068 [P] Add API usage examples to README.md (curl commands for each endpoint)
- [ ] T069 Run full test suite and ensure >80% code coverage (pytest --cov=src --cov-report=html)
- [ ] T070 [P] Add request/response logging for debugging
- [ ] T071 [P] Validate all edge cases from spec.md (invalid foreign keys, malformed JSON, negative amounts, etc.)
- [ ] T072 Generate and review FastAPI automatic OpenAPI docs at /docs endpoint
- [ ] T073 [P] Performance testing for latency targets (<200ms simple CRUD, <1s filtered lists)
- [ ] T074 Final code review against constitution principles (single responsibility, no premature abstractions, boring solutions)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 4 - Accounts (Phase 3)**: Depends on Foundational - BLOCKS US1 (transactions need accounts)
- **User Story 6 - Reference Data (Phase 4)**: Depends on Foundational - Can run in parallel with US4
- **User Story 1 - Create/Retrieve (Phase 5)**: Depends on Foundational + US4 (accounts must exist)
- **User Story 2 - Update/Delete (Phase 6)**: Depends on US1 completion
- **User Story 3 - List/Filter (Phase 7)**: Depends on US1 completion (can run parallel with US2)
- **User Story 5 - Categories/Payees (Phase 8)**: Depends on Foundational - Can run in parallel with US1-3
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Setup (Phase 1)
    ↓
Foundational (Phase 2) ← CRITICAL BLOCKER
    ↓
    ├─→ US4: Accounts (Phase 3) ← REQUIRED for transactions
    │       ↓
    │   US1: Create/Retrieve Transaction (Phase 5) ← Core MVP
    │       ↓
    │       ├─→ US2: Update/Delete Transaction (Phase 6)
    │       └─→ US3: List/Filter Transactions (Phase 7)
    │
    ├─→ US6: Reference Data (Phase 4) ← Simple, no dependencies
    └─→ US5: Categories/Payees (Phase 8) ← Optional enhancement
            ↓
        Polish (Phase 9)
```

### Within Each User Story

- Models before services (T016 → T020)
- Schemas parallel with models (T017-T019 parallel to T014-T016)
- Services before routers (T020 → T021)
- Router implementation before registration (T021 → T022)
- Core implementation before tests (T021-T023 → T024-T025)
- Unit tests parallel with integration tests (T024 || T025)

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks can run sequentially (fast, file creation)
- T005 [P] and T006 [P] can run parallel after T001-T004

**Phase 2 (Foundational)**: Some tasks can run in parallel
- T010 [P] and T011 [P] can run parallel with T007-T009
- T012 [P] can run parallel with T007-T011

**Phase 3 (US4 - Accounts)**:
- T014 [P] and T015 [P] can run in parallel (different models)
- T017 [P] and T018 [P] can run in parallel (different schemas)
- T024 [P] can start as soon as T020 completes (parallel with T021-T023)

**Phase 4 (US6 - Reference)**:
- T026 [P] can run parallel with Phase 3 if resources available
- All US6 tasks (T026-T029) can run parallel to other user stories

**Phase 5 (US1 - Create/Retrieve)**:
- T030 [P] and T031 [P] can run in parallel (different models)
- T033 [P] and T034 [P] can run in parallel (different schemas)
- T040 [P] can start as soon as T036 completes

**Phase 8 (US5 - Categories/Payees)**: Highly parallel
- T054-T059 all marked [P] - can run simultaneously
- T061-T064 all marked [P] - can run simultaneously

**Phase 9 (Polish)**: Many parallel opportunities
- T065-T068, T070-T071, T073 all marked [P]

---

## Parallel Example: User Story 4 (Accounts)

```bash
# Start Phase 3 models in parallel:
Task: T014 [P] [US4] Create Currency model in src/models/currency.py
Task: T015 [P] [US4] Create AccountType model in src/models/account_type.py

# Then Account model (depends on Currency and AccountType):
Task: T016 [US4] Create Account model in src/models/account.py

# Create schemas in parallel:
Task: T017 [P] [US4] Create Currency response schema
Task: T018 [P] [US4] Create AccountType response schema

# Then Account schemas (depends on above):
Task: T019 [US4] Create Account schemas

# After service is implemented, tests can run in parallel:
Task: T024 [P] [US4] Write unit tests
Task: T025 [US4] Write integration tests (sequential after T024 for data setup)
```

---

## Parallel Example: User Story 1 (Transactions)

```bash
# Create models in parallel:
Task: T030 [P] [US1] Create Category model
Task: T031 [P] [US1] Create Payee model

# Then Transaction model (depends on Category and Payee):
Task: T032 [US1] Create Transaction model

# Create schemas in parallel:
Task: T033 [P] [US1] Create Category schemas
Task: T034 [P] [US1] Create Payee schemas

# Then Transaction schemas:
Task: T035 [US1] Create Transaction schemas

# After service implemented, tests in parallel:
Task: T040 [P] [US1] Write unit tests
Task: T041 [US1] Write integration tests
```

---

## Implementation Strategy

### MVP First (Phases 1-5 Only)

1. **Phase 1**: Setup (T001-T006) - ~30 minutes
2. **Phase 2**: Foundational (T007-T013) - ~1 hour
3. **Phase 3**: US4 Accounts (T014-T025) - ~2 hours
4. **Phase 4**: US6 Reference Data (T026-T029) - ~30 minutes
5. **Phase 5**: US1 Create/Retrieve Transaction (T030-T041) - ~2.5 hours

**Total MVP Time**: ~6.5 hours

**STOP and VALIDATE**: At this point you have:
- ✅ Accounts can be created and managed
- ✅ Reference data accessible
- ✅ Transactions can be created and retrieved
- ✅ Account balances automatically maintained
- ✅ Core expense tracking functionality working

Deploy this MVP and validate with real users before continuing!

### Incremental Delivery (Add Features Progressively)

**After MVP is validated**:

6. **Phase 6**: US2 Update/Delete (T042-T047) - ~1.5 hours
   - Now users can correct mistakes

7. **Phase 7**: US3 List/Filter (T048-T053) - ~2 hours
   - Now users can analyze spending patterns

8. **Phase 8**: US5 Categories/Payees (T054-T064) - ~3 hours
   - Now users can organize and categorize expenses

9. **Phase 9**: Polish (T065-T074) - ~2 hours
   - Production-ready refinements

**Total Complete Implementation**: ~15 hours

### Parallel Team Strategy

With 3 developers after Foundational (Phase 2) completes:

- **Developer A**: Phase 3 (US4 Accounts) → Phase 5 (US1 Transactions)
- **Developer B**: Phase 4 (US6 Reference) → Phase 6 (US2 Update/Delete) → Phase 7 (US3 List/Filter)
- **Developer C**: Phase 8 (US5 Categories/Payees) → Phase 9 (Polish)

Stories complete independently and integrate seamlessly.

---

## Task Execution Checklist

Before marking a task complete, verify:

- [ ] Code compiles and runs without errors
- [ ] File is in the correct location per plan.md structure
- [ ] Imports are correct and no circular dependencies
- [ ] Type hints used throughout (per Python best practices)
- [ ] Error handling implemented where appropriate
- [ ] Database operations use proper session management
- [ ] Foreign key constraints respected
- [ ] Validation logic matches data-model.md and OpenAPI spec
- [ ] Tests pass (if applicable)
- [ ] Manual testing via /docs endpoint successful (for routers)
- [ ] Code follows single responsibility principle
- [ ] No premature abstractions introduced

---

## Notes

- **[P]** tasks = different files, no dependencies - can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each logical group of tasks (e.g., after completing a model + schema + service)
- Stop at any checkpoint to validate story independently
- Database triggers handle balance calculations - don't implement in application code
- Transfer transactions (`transaction_type='transfer'`) are OUT OF SCOPE
- Use exact database column names (transaction_id, account_id, etc.) not generic "id"
- All validation rules from data-model.md must be implemented in Pydantic schemas
- Refer to contracts/openapi.yaml for exact endpoint specifications

---

## Summary

- **Total Tasks**: 74
- **MVP Tasks (Phases 1-5)**: 41 tasks
- **Setup**: 6 tasks
- **Foundational**: 7 tasks
- **US4 (Accounts)**: 12 tasks
- **US6 (Reference)**: 4 tasks
- **US1 (Create/Retrieve)**: 12 tasks
- **US2 (Update/Delete)**: 6 tasks
- **US3 (List/Filter)**: 6 tasks
- **US5 (Categories/Payees)**: 11 tasks
- **Polish**: 10 tasks

**Parallel Task Count**: 28 tasks marked [P] can run concurrently

**Independent Test Criteria**:
- US4: Create account → Retrieve account → List accounts
- US6: GET /account-types → GET /currencies
- US1: POST transaction → GET transaction by ID → Verify 404 for non-existent
- US2: PATCH transaction → GET updated → DELETE → Verify 404
- US3: Create multiple transactions → GET with filters → Verify pagination
- US5: POST category → GET category → POST payee → GET payee

**Suggested MVP**: Phases 1-5 (41 tasks, ~6.5 hours) - Delivers core expense tracking with account and transaction management
