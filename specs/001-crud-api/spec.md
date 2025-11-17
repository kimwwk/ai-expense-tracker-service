# Feature Specification: Basic CRUD REST API for Expense Tracking

**Feature Branch**: `001-crud-api`
**Created**: 2025-11-16
**Status**: Draft
**Input**: User description: "Basic CRUD REST API for expense tracking with transactions, accounts, categories, and payees endpoints"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Retrieve Transaction (Priority: P1)

A user needs to record a new expense transaction and retrieve it to verify the details were saved correctly.

**Why this priority**: Recording transactions is the core functionality of an expense tracking system. Without this, the system has no purpose. This represents the minimal viable product.

**Independent Test**: Can be fully tested by sending a POST request with transaction data, receiving a 201 response with the created transaction, then sending a GET request to retrieve the same transaction by ID. Delivers immediate value by allowing basic expense recording.

**Acceptance Scenarios**:

1. **Given** no existing transactions, **When** I POST a new transaction with valid data (amount, date, account_id), **Then** I receive a 201 Created response with the transaction details and a Location header
2. **Given** a transaction exists with ID 123, **When** I GET /transactions/123, **Then** I receive a 200 OK response with the complete transaction details
3. **Given** I request a non-existent transaction ID, **When** I GET /transactions/999, **Then** I receive a 404 Not Found response with an appropriate error message

---

### User Story 2 - Update and Delete Transaction (Priority: P2)

A user needs to correct errors in previously recorded transactions or remove transactions that were recorded by mistake.

**Why this priority**: Once users can create transactions, they immediately need to fix mistakes. This is essential for data accuracy but secondary to initial recording capability.

**Independent Test**: Can be fully tested by creating a transaction, sending a PATCH request to modify specific fields, verifying the changes with a GET request, then sending a DELETE request and confirming the transaction no longer exists. Delivers value by ensuring data accuracy.

**Acceptance Scenarios**:

1. **Given** a transaction exists with amount 50.00, **When** I PATCH the transaction with amount 55.00, **Then** I receive a 200 OK response with the updated transaction showing 55.00
2. **Given** a transaction exists, **When** I PUT the transaction with complete new data, **Then** I receive a 200 OK response with all fields updated
3. **Given** a transaction exists with ID 123, **When** I DELETE /transactions/123, **Then** I receive a 204 No Content response and subsequent GET requests return 404

---

### User Story 3 - List and Filter Transactions (Priority: P2)

A user needs to view all their transactions with the ability to filter by date range, account, category, or status to analyze spending patterns.

**Why this priority**: Listing and filtering enables users to make sense of their transaction history. Critical for usability but requires basic CRUD operations to exist first.

**Independent Test**: Can be fully tested by creating multiple transactions with different attributes, then sending GET requests with various query parameters (date range, account_id, category_id) and verifying the filtered results. Delivers value by enabling expense analysis.

**Acceptance Scenarios**:

1. **Given** 150 transactions exist, **When** I GET /transactions with no parameters, **Then** I receive a 200 OK response with the first 50 transactions (default limit) and pagination metadata showing total: 150
2. **Given** transactions exist for multiple accounts, **When** I GET /transactions?account_id=5, **Then** I receive only transactions for account 5
3. **Given** transactions exist across multiple months, **When** I GET /transactions?start_date=2025-01-01&end_date=2025-01-31, **Then** I receive only transactions within January 2025
4. **Given** transactions exist, **When** I GET /transactions?limit=10&offset=20, **Then** I receive transactions 21-30 with pagination metadata

---

### User Story 4 - Manage Accounts (Priority: P1)

A user needs to create accounts (bank accounts, credit cards, cash) and retrieve account information to organize their transactions.

**Why this priority**: Accounts are required before transactions can be created (foreign key dependency). This is foundational infrastructure that must exist for the system to function.

**Independent Test**: Can be fully tested by creating an account with POST, retrieving it with GET, listing all accounts, and verifying the account structure. Delivers value by establishing the organizational structure for tracking expenses.

**Acceptance Scenarios**:

1. **Given** no existing accounts, **When** I POST a new account with name "Chase Checking", account_type_id 1, and currency "USD", **Then** I receive a 201 Created response with the account details
2. **Given** an account exists, **When** I GET /accounts/{id}, **Then** I receive a 200 OK response with the account details including current balance
3. **Given** multiple accounts exist, **When** I GET /accounts, **Then** I receive a 200 OK response with all accounts and pagination metadata

---

### User Story 5 - Manage Categories and Payees (Priority: P3)

A user needs to create and manage expense categories (groceries, utilities, entertainment) and payees (merchants, vendors) to classify and organize transactions.

**Why this priority**: While useful for organization, categories and payees are optional for basic transaction tracking. Users can function with uncategorized transactions initially.

**Independent Test**: Can be fully tested by creating categories and payees via POST, retrieving them via GET, and later associating them with transactions. Delivers value by enabling expense categorization and analysis.

**Acceptance Scenarios**:

1. **Given** no existing categories, **When** I POST a new category with name "Groceries" and category_type "expense", **Then** I receive a 201 Created response with the category details
2. **Given** categories exist, **When** I GET /categories, **Then** I receive a 200 OK response with all active categories
3. **Given** no existing payees, **When** I POST a new payee with name "Whole Foods", **Then** I receive a 201 Created response with the payee details
4. **Given** payees exist, **When** I GET /payees, **Then** I receive a 200 OK response with all active payees

---

### User Story 6 - Access Reference Data (Priority: P3)

A user or client application needs to retrieve available account types and currencies to populate dropdown menus and ensure data consistency.

**Why this priority**: Reference data supports the user interface but is not critical functionality. Hard-coded defaults can work initially.

**Independent Test**: Can be fully tested by sending GET requests to reference endpoints and verifying the standard data is returned. Delivers value by supporting dynamic UI generation.

**Acceptance Scenarios**:

1. **Given** the system is running, **When** I GET /account-types, **Then** I receive a 200 OK response with all available account types (checking, savings, credit card, etc.)
2. **Given** the system is running, **When** I GET /currencies, **Then** I receive a 200 OK response with all supported currencies (USD, EUR, GBP, etc.)

---

### Edge Cases

- What happens when a user attempts to create a transaction with an invalid or non-existent account_id?
- What happens when a user attempts to delete an account that has associated transactions?
- How does the system handle requests with invalid date formats (non-ISO 8601)?
- What happens when pagination parameters exceed reasonable bounds (e.g., limit=10000)?
- How does the system respond to requests with negative amounts?
- What happens when a user attempts to update a transaction with invalid enum values (e.g., invalid transaction_type or status)?
- How does the system handle concurrent updates to the same transaction?
- What happens when required fields are missing in POST/PUT requests?
- How does the system respond to malformed JSON in request bodies?
- What happens when a user attempts to create duplicate categories or payees with the same name?

## Requirements *(mandatory)*

### Functional Requirements

#### Transaction Management

- **FR-001**: System MUST allow clients to create a new transaction via POST /transactions with required fields (amount, transaction_date, account_id) and optional fields (category_id, payee_id, transaction_type, status, description)
- **FR-002**: System MUST return 201 Created with the created transaction and Location header pointing to the new resource
- **FR-003**: System MUST allow clients to retrieve a single transaction by ID via GET /transactions/:id
- **FR-004**: System MUST allow clients to list transactions via GET /transactions with optional filtering by account_id, category_id, payee_id, transaction_type, status, start_date, end_date
- **FR-005**: System MUST support pagination for transaction lists using limit (default 50, max 100) and offset (default 0) parameters
- **FR-006**: System MUST allow clients to fully update a transaction via PUT /transactions/:id
- **FR-007**: System MUST allow clients to partially update a transaction via PATCH /transactions/:id
- **FR-008**: System MUST allow clients to delete a transaction via DELETE /transactions/:id
- **FR-009**: System MUST validate that amount values are positive decimals
- **FR-010**: System MUST validate that transaction_date is a valid ISO 8601 date
- **FR-011**: System MUST validate that transaction_type and status match allowed enum values
- **FR-012**: System MUST validate that foreign keys (account_id, category_id, payee_id) reference existing records

#### Account Management

- **FR-013**: System MUST allow clients to create a new account via POST /accounts with required fields (account_name, account_type_id, currency_code)
- **FR-014**: System MUST return 201 Created with the created account
- **FR-015**: System MUST allow clients to retrieve a single account by ID via GET /accounts/:id including current balance
- **FR-016**: System MUST allow clients to list accounts via GET /accounts with optional filtering by account_type_id, is_closed, currency_code
- **FR-017**: System MUST support pagination for account lists using limit and offset parameters
- **FR-018**: System MUST allow clients to fully update an account via PUT /accounts/:id
- **FR-019**: System MUST allow clients to partially update an account via PATCH /accounts/:id
- **FR-020**: System MUST allow clients to delete an account via DELETE /accounts/:id
- **FR-021**: System MUST validate that account_type_id references an existing account type
- **FR-022**: System MUST validate that currency_code is a valid 3-letter ISO currency code

#### Category Management

- **FR-023**: System MUST allow clients to create a new category via POST /categories with required fields (category_name, category_type)
- **FR-024**: System MUST return 201 Created with the created category
- **FR-025**: System MUST allow clients to retrieve a single category by ID via GET /categories/:id
- **FR-026**: System MUST allow clients to list categories via GET /categories with optional filtering by category_type, category_group, is_active
- **FR-027**: System MUST support pagination for category lists using limit and offset parameters
- **FR-028**: System MUST allow clients to fully update a category via PUT /categories/:id
- **FR-029**: System MUST allow clients to partially update a category via PATCH /categories/:id
- **FR-030**: System MUST allow clients to delete a category via DELETE /categories/:id

#### Payee Management

- **FR-031**: System MUST allow clients to create a new payee via POST /payees with required field (payee_name)
- **FR-032**: System MUST return 201 Created with the created payee
- **FR-033**: System MUST allow clients to retrieve a single payee by ID via GET /payees/:id
- **FR-034**: System MUST allow clients to list payees via GET /payees with optional filtering by is_active
- **FR-035**: System MUST support pagination for payee lists using limit and offset parameters
- **FR-036**: System MUST allow clients to fully update a payee via PUT /payees/:id
- **FR-037**: System MUST allow clients to partially update a payee via PATCH /payees/:id
- **FR-038**: System MUST allow clients to delete a payee via DELETE /payees/:id

#### Reference Data

- **FR-039**: System MUST provide read-only access to account types via GET /account-types
- **FR-040**: System MUST provide read-only access to currencies via GET /currencies

#### Data Validation & Error Handling

- **FR-041**: System MUST return 400 Bad Request for malformed JSON or invalid request format
- **FR-042**: System MUST return 404 Not Found when requested resource does not exist
- **FR-043**: System MUST return 422 Unprocessable Entity when validation fails (e.g., invalid foreign key, negative amount)
- **FR-044**: System MUST return 500 Internal Server Error for unexpected system failures
- **FR-045**: System MUST return error responses in consistent JSON format with error code, message, and optional details object
- **FR-046**: System MUST validate that all required fields are present in POST and PUT requests
- **FR-047**: System MUST validate field types match expected schema (string, number, date, enum)

#### Response Format

- **FR-048**: System MUST use application/json content type for all requests and responses
- **FR-049**: System MUST use snake_case for all JSON field names
- **FR-050**: System MUST include pagination metadata (limit, offset, total) in list endpoint responses
- **FR-051**: System MUST return 204 No Content for successful DELETE operations with no response body
- **FR-052**: System MUST return updated resource in PUT/PATCH response body with 200 OK status

#### Sorting & Filtering

- **FR-053**: System MUST support sorting via sort and order query parameters (default: descending by ID)
- **FR-054**: System MUST support date range filtering using ISO 8601 formatted start_date and end_date parameters

### Key Entities *(include if feature involves data)*

- **Transaction**: Represents a financial transaction (expense or income). Key attributes include amount, transaction date, account reference, optional category and payee references, transaction type (debit/credit), status (pending/cleared/reconciled), and description. Related to Account (required), Category (optional), and Payee (optional).

- **Account**: Represents a financial account (checking, savings, credit card, cash, etc.). Key attributes include account name, account type reference, currency code, opening balance, current balance, and is_closed status. Related to Account Type (required) and has many Transactions.

- **Category**: Represents an expense or income category for classification. Key attributes include category name, category type (expense/income), optional category group for hierarchical organization, and is_active status. Related to many Transactions.

- **Payee**: Represents a merchant, vendor, or entity involved in transactions. Key attributes include payee name and is_active status. Related to many Transactions.

- **Account Type**: Reference data representing types of accounts (checking, savings, credit card, loan, investment, cash). Read-only reference data.

- **Currency**: Reference data representing supported currencies with ISO 4217 currency codes. Read-only reference data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Clients can successfully create and retrieve any resource (transaction, account, category, payee) within 2 seconds under normal load
- **SC-002**: System correctly validates 100% of invalid requests and returns appropriate error responses (400, 404, 422) with clear error messages
- **SC-003**: System handles at least 100 concurrent API requests without errors or performance degradation
- **SC-004**: All list endpoints return paginated results correctly with accurate pagination metadata when total records exceed the page limit
- **SC-005**: Filtering operations return only records matching the specified criteria with 100% accuracy
- **SC-006**: Foreign key validation prevents 100% of attempts to create transactions with invalid account_id, category_id, or payee_id
- **SC-007**: All CRUD operations follow REST conventions with correct HTTP methods and status codes in 100% of cases
- **SC-008**: Database triggers correctly maintain account balances after transaction creation, updates, and deletions with 100% accuracy
- **SC-009**: Date range filtering correctly handles edge cases (same start/end date, invalid ranges) and returns accurate results
- **SC-010**: System supports at least 10,000 transactions per account without performance degradation in list operations

## Assumptions

1. **Database Schema Exists**: The PostgreSQL database schema is already created with all necessary tables, foreign key constraints, and triggers for account balance management.

2. **Single User Context**: This API does not implement user authentication or multi-tenancy. All resources are accessible to any client without authorization checks. User/tenant isolation will be added in a future feature.

3. **Database Handles Business Logic**: Complex business logic such as account balance calculations and data integrity constraints are handled by database triggers and constraints, not application code.

4. **Synchronous Operations**: All operations are synchronous. No background processing, queuing, or asynchronous workflows are required.

5. **Standard Currency Handling**: The system stores amounts as decimal values and relies on the database for precision. Currency conversion is not supported.

6. **No File Uploads**: Transaction receipts, attachments, or document uploads are not part of this feature.

7. **Basic Error Handling**: Error responses provide clear messages for debugging but do not include sensitive system information or stack traces.

8. **Database Connection Management**: Connection pooling and database connection management is handled by the underlying database client library with standard defaults.

9. **No Caching**: Response caching is not implemented. All requests query the database directly.

10. **ISO Standards**: All dates use ISO 8601 format (YYYY-MM-DD), all currencies use ISO 4217 codes, and all timestamps are stored in UTC.
