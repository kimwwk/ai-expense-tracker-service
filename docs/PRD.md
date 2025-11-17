# Product Requirements Document
## AI Expense Tracker Service

### 1. Purpose
Provide basic CRUD operations for expense tracking data. Serve as a simple data access layer over the PostgreSQL database.

### 2. REST API Endpoints

#### 2.1 Transactions
- `POST /transactions` - Create a single transaction
- `GET /transactions/:id` - Get a single transaction by ID
- `GET /transactions` - List transactions with optional query parameters
  - Query params: `account_id`, `category_id`, `payee_id`, `transaction_type`, `status`, `start_date`, `end_date`, `limit`, `offset`
- `PUT /transactions/:id` - Update a single transaction (full update)
- `PATCH /transactions/:id` - Partial update of a transaction
- `DELETE /transactions/:id` - Delete a single transaction

#### 2.2 Accounts
- `POST /accounts` - Create a new account
- `GET /accounts/:id` - Get a single account by ID
- `GET /accounts` - List accounts with optional query parameters
  - Query params: `account_type_id`, `is_closed`, `currency_code`
- `PUT /accounts/:id` - Update account (full update)
- `PATCH /accounts/:id` - Partial update of account
- `DELETE /accounts/:id` - Delete an account

#### 2.3 Categories
- `POST /categories` - Create a new category
- `GET /categories/:id` - Get a single category by ID
- `GET /categories` - List categories with optional query parameters
  - Query params: `category_type`, `category_group`, `is_active`
- `PUT /categories/:id` - Update category (full update)
- `PATCH /categories/:id` - Partial update of category
- `DELETE /categories/:id` - Delete a category

#### 2.4 Payees
- `POST /payees` - Create a new payee
- `GET /payees/:id` - Get a single payee by ID
- `GET /payees` - List payees with optional query parameters
  - Query params: `is_active`
- `PUT /payees/:id` - Update payee (full update)
- `PATCH /payees/:id` - Partial update of payee
- `DELETE /payees/:id` - Delete a payee

#### 2.5 Reference Data (Read-only)
- `GET /account-types` - List all account types
- `GET /currencies` - List all currencies

### 3. API Design Principles

#### 3.1 HTTP Methods & Status Codes
- `POST` - Create resource → `201 Created` (with `Location` header)
- `GET` - Read resource(s) → `200 OK`
- `PUT` - Full update → `200 OK` or `204 No Content`
- `PATCH` - Partial update → `200 OK` or `204 No Content`
- `DELETE` - Remove resource → `204 No Content`
- Errors → `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`

#### 3.2 Request/Response Format
- Content-Type: `application/json`
- Use snake_case for JSON field names (matches database schema)
- Return created resource in POST response body
- Return updated resource in PUT/PATCH response body (or 204 with no body)
- DELETE returns empty body with 204 status

#### 3.3 Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid transaction amount",
    "details": {
      "field": "amount",
      "reason": "must be positive"
    }
  }
}
```

#### 3.4 List Endpoints
- Support pagination: `limit` (default 50, max 100) and `offset` (default 0)
- Response format:
```json
{
  "data": [...],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 150
  }
}
```

#### 3.5 Filtering & Sorting
- Use query parameters for filters (e.g., `?account_id=1&status=cleared`)
- Support sorting: `?sort=transaction_date&order=desc` (default: desc by ID)
- Date filters use ISO 8601 format: `?start_date=2025-01-01&end_date=2025-01-31`

#### 3.6 Idempotency
- GET, PUT, DELETE are naturally idempotent
- POST should validate duplicates where appropriate

### 4. Validation Rules

#### 4.1 Request Validation
- Required fields must be present
- Field types must match schema (string, number, date, enum)
- Foreign keys must reference existing records
- Amounts must be positive decimals
- Dates must be valid ISO 8601 format
- Enum values must match allowed values (transaction_type, status, etc.)

#### 4.2 Business Rules (enforced by database)
- Account balance updates handled by triggers
- Cascade deletes handled by foreign key constraints
- Timestamps (created_at, updated_at) managed by database

### 5. Key Principles
- **RESTful design**: Resource-oriented URLs, proper HTTP methods and status codes
- **Simple CRUD only**: No business logic, no aggregations, no complex queries
- **Database handles complexity**: Triggers maintain balances, constraints enforce integrity
- **Thin layer**: Validate input, execute database operation, return result
- **Consistent responses**: Uniform error format, pagination, and field naming

### 6. Success Criteria
- All CRUD operations follow REST conventions
- Proper HTTP status codes returned
- Input validation prevents invalid data from reaching database
- Clear, consistent error messages
- List endpoints support filtering and pagination
- Database constraints and triggers work as designed
