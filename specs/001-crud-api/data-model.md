# Data Model Design

**Feature**: Basic CRUD REST API for Expense Tracking
**Date**: 2025-11-16
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the data model for the expense tracking API based on the existing PostgreSQL schema in the `PostgreSQL-migrations` folder. The API provides CRUD operations over the existing database structure.

**Source**: Schema defined in `../ai-expense-tracker-agent/PostgreSQL-migrations/`
- `20250725-init.sql` - Initial schema
- `20250818-01-balance-management-schema.sql` - Balance management enhancements
- `20250818-02-balance-triggers.sql` - Automatic balance triggers
- `20250818-03-balance-helper-functions.sql` - Helper functions

## Database Schema Overview

**Note**: The PostgreSQL database schema already exists with:
- All tables, columns, indexes, and constraints
- Foreign key constraints for referential integrity
- Database triggers for automatic balance calculations
- Timestamp management via triggers (updated_at)
- Helper functions for balance validation and reconciliation

**Transfer Transaction Scope**: Transfer transactions (`transaction_type='transfer'` with `transfer_account_id`) are **OUT OF SCOPE** for this initial CRUD API. The API will support `income` and `expense` types only.

## Entity Definitions

### 1. Transaction

**Purpose**: Represents a financial transaction (expense or income)

**Database Table**: `transactions`

**Primary Key**: `transaction_id` (SERIAL)

**SQLAlchemy Model Fields**:
```python
class Transaction(Base):
    __tablename__ = "transactions"

    # Primary Key
    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), ForeignKey("currencies.currency_code"), nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="cleared")

    # Optional Fields
    payee_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("payees.payee_id"), nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.category_id"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False, default=1.000000)
    transfer_account_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("accounts.account_id"), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps (managed by database triggers)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    account: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="transactions")
    payee: Mapped[Optional["Payee"]] = relationship("Payee", back_populates="transactions")
    currency: Mapped["Currency"] = relationship("Currency")
```

**Pydantic Schemas**:
```python
# Request schema for creating transaction
class TransactionCreate(BaseModel):
    # Required fields
    account_id: int
    transaction_type: Literal["income", "expense"]  # NOTE: 'transfer' is OUT OF SCOPE
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    currency_code: str = Field(pattern=r"^[A-Z]{3}$")
    base_amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    transaction_date: date

    # Optional fields with defaults
    status: Optional[Literal["pending", "cleared", "reconciled", "void"]] = "cleared"
    exchange_rate: Optional[Decimal] = Field(1.000000, max_digits=10, decimal_places=6)

    # Optional fields
    payee_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=255)
    reference_number: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

# Request schema for updating transaction (partial update)
class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    transaction_type: Optional[Literal["income", "expense"]] = None
    amount: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)
    currency_code: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    base_amount: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)
    transaction_date: Optional[date] = None
    status: Optional[Literal["pending", "cleared", "reconciled", "void"]] = None
    exchange_rate: Optional[Decimal] = Field(None, max_digits=10, decimal_places=6)
    payee_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=255)
    reference_number: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

# Response schema
class TransactionResponse(BaseModel):
    transaction_id: int
    account_id: int
    transaction_type: str
    amount: Decimal
    currency_code: str
    base_amount: Decimal
    transaction_date: date
    status: str
    exchange_rate: Decimal
    payee_id: Optional[int]
    category_id: Optional[int]
    description: Optional[str]
    reference_number: Optional[str]
    transfer_account_id: Optional[int]  # Exposed but read-only (no create/update for transfers)
    location: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Database Constraints**:
- `CHECK (transaction_type IN ('income', 'expense', 'transfer'))` - API only allows income/expense
- `CHECK (status IN ('pending', 'cleared', 'reconciled', 'void'))`
- Amount must be positive (enforced by Pydantic validation)
- Foreign key constraints on account_id, category_id, payee_id, currency_code

**Indexes** (from schema):
- `idx_account_date` on (account_id, transaction_date)
- `idx_category_date` on (category_id, transaction_date)
- `idx_transaction_date` on (transaction_date)

**Validation Rules**:
- Amount must be positive decimal
- Transaction date must be valid ISO 8601 date
- Transaction type must be 'income' or 'expense' (API restriction)
- Status must match allowed values
- Foreign keys must reference existing records

**Relationships**:
- Many-to-One with Account (required)
- Many-to-One with Category (optional)
- Many-to-One with Payee (optional)
- Many-to-One with Currency (required)

**Note**: Balance updates are handled automatically by database trigger `maintain_account_balance()` on INSERT/UPDATE/DELETE.

### 2. Account

**Purpose**: Represents a financial account (bank account, credit card, cash, etc.)

**Database Table**: `accounts`

**Primary Key**: `account_id` (SERIAL)

**SQLAlchemy Model Fields**:
```python
class Account(Base):
    __tablename__ = "accounts"

    # Primary Key
    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    account_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("account_types.account_type_id"), nullable=False)
    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), ForeignKey("currencies.currency_code"), nullable=False, default="USD")
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0.00)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0.00)

    # Optional Fields
    account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    institution_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    opening_balance_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    account_type: Mapped["AccountType"] = relationship("AccountType")
    currency: Mapped["Currency"] = relationship("Currency")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="account")
```

**Pydantic Schemas**:
```python
class AccountCreate(BaseModel):
    # Required fields
    account_type_id: int
    account_name: str = Field(min_length=1, max_length=100)
    currency_code: str = Field(pattern=r"^[A-Z]{3}$", default="USD")
    opening_balance: Decimal = Field(default=0.00, max_digits=15, decimal_places=2)

    # Optional fields with defaults
    is_closed: bool = False
    opening_balance_date: Optional[date] = None  # Defaults to current date in DB

    # Optional fields
    account_number: Optional[str] = Field(None, max_length=50)
    institution_name: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    notes: Optional[str] = None

class AccountUpdate(BaseModel):
    account_type_id: Optional[int] = None
    account_name: Optional[str] = Field(None, min_length=1, max_length=100)
    currency_code: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    account_number: Optional[str] = Field(None, max_length=50)
    institution_name: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    is_closed: Optional[bool] = None
    notes: Optional[str] = None
    # Note: opening_balance and opening_balance_date should not be updated via API

class AccountResponse(BaseModel):
    account_id: int
    account_type_id: int
    account_name: str
    account_number: Optional[str]
    institution_name: Optional[str]
    currency_code: str
    opening_balance: Decimal
    current_balance: Decimal
    credit_limit: Optional[Decimal]
    is_closed: bool
    notes: Optional[str]
    opening_balance_date: date
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Database Constraints**:
- `CHECK (opening_balance_date <= CURRENT_DATE)` - Opening balance date cannot be in future
- Foreign keys on account_type_id, currency_code

**Validation Rules**:
- account_type_id must reference existing account type
- currency_code must be valid 3-letter ISO 4217 code
- Account name required and non-empty
- Opening balance date cannot be future date

**Relationships**:
- Many-to-One with AccountType (required)
- Many-to-One with Currency (required)
- One-to-Many with Transactions

**Note**: `current_balance` is maintained automatically by database triggers and should be treated as read-only in the API.

### 3. Category

**Purpose**: Represents an expense or income category for classification

**Database Table**: `categories`

**Primary Key**: `category_id` (SERIAL)

**SQLAlchemy Model Fields**:
```python
class Category(Base):
    __tablename__ = "categories"

    # Primary Key
    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Optional Fields
    category_group: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color_code: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    icon_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="category")
```

**Pydantic Schemas**:
```python
class CategoryCreate(BaseModel):
    # Required fields
    category_name: str = Field(min_length=1, max_length=100)
    category_type: Literal["income", "expense", "transfer"]

    # Optional fields
    category_group: Optional[str] = Field(None, max_length=50)
    color_code: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")  # Hex color
    icon_name: Optional[str] = Field(None, max_length=50)
    is_active: bool = True

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_type: Optional[Literal["income", "expense", "transfer"]] = None
    category_group: Optional[str] = Field(None, max_length=50)
    color_code: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    category_type: str
    category_group: Optional[str]
    color_code: Optional[str]
    icon_name: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Database Constraints**:
- `CHECK (category_type IN ('income', 'expense', 'transfer'))`

**Indexes** (from schema):
- `idx_category_type` on (category_type)
- `idx_category_group` on (category_group)

**Validation Rules**:
- Category name required and non-empty
- Category type must be 'income', 'expense', or 'transfer'
- Color code must be valid hex format if provided

**Relationships**:
- One-to-Many with Transactions

### 4. Payee

**Purpose**: Represents a merchant, vendor, or entity involved in transactions

**Database Table**: `payees`

**Primary Key**: `payee_id` (SERIAL)

**SQLAlchemy Model Fields**:
```python
class Payee(Base):
    __tablename__ = "payees"

    # Primary Key
    payee_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    payee_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Optional Fields
    default_category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.category_id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    default_category: Mapped[Optional["Category"]] = relationship("Category")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="payee")
```

**Pydantic Schemas**:
```python
class PayeeCreate(BaseModel):
    # Required fields
    payee_name: str = Field(min_length=1, max_length=100)

    # Optional fields
    default_category_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool = True

class PayeeUpdate(BaseModel):
    payee_name: Optional[str] = Field(None, min_length=1, max_length=100)
    default_category_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class PayeeResponse(BaseModel):
    payee_id: int
    payee_name: str
    default_category_id: Optional[int]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Indexes** (from schema):
- `idx_payee_name` on (payee_name)

**Validation Rules**:
- Payee name required and non-empty
- default_category_id must reference existing category if provided

**Relationships**:
- Many-to-One with Category (optional, for default category)
- One-to-Many with Transactions

### 5. AccountType (Reference Data)

**Purpose**: Reference data representing types of accounts

**Database Table**: `account_types`

**Primary Key**: `account_type_id` (SERIAL)

**SQLAlchemy Model Fields**:
```python
class AccountType(Base):
    __tablename__ = "account_types"

    # Primary Key
    account_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    type_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    is_asset: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Optional Fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

**Pydantic Schema**:
```python
class AccountTypeResponse(BaseModel):
    account_type_id: int
    type_name: str
    description: Optional[str]
    is_asset: bool

    model_config = ConfigDict(from_attributes=True)
```

**Note**: Read-only reference data. No create/update/delete operations.

**Seeded Values** (from schema):
- checking (asset)
- savings (asset)
- credit_card (liability)
- cash (asset)
- investment (asset)
- loan (liability)

### 6. Currency (Reference Data)

**Purpose**: Reference data representing supported currencies

**Database Table**: `currencies`

**Primary Key**: `currency_code` (CHAR(3))

**SQLAlchemy Model Fields**:
```python
class Currency(Base):
    __tablename__ = "currencies"

    # Primary Key
    currency_code: Mapped[str] = mapped_column(String(3), primary_key=True)

    # Required Fields
    currency_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Optional Fields
    currency_symbol: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    decimal_places: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

**Pydantic Schema**:
```python
class CurrencyResponse(BaseModel):
    currency_code: str
    currency_name: str
    currency_symbol: Optional[str]
    decimal_places: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
```

**Note**: Read-only reference data. No create/update/delete operations.

**Seeded Values** (from schema):
- USD (US Dollar, $)
- GBP (British Pound, £)
- CAD (Canadian Dollar, C$)

## Common Schemas

### Pagination

**Purpose**: Consistent pagination across all list endpoints

```python
class PaginationMetadata(BaseModel):
    limit: int
    offset: int
    total: int

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: PaginationMetadata
```

**Usage Example**:
```python
PaginatedResponse[TransactionResponse]  # Paginated transaction list
PaginatedResponse[AccountResponse]      # Paginated account list
```

**Default Values**:
- limit: default=50, max=100
- offset: default=0

### Error Responses

**Purpose**: Consistent error format across all endpoints (per PRD section 3.3)

```python
class ErrorDetail(BaseModel):
    field: Optional[str] = None
    reason: Optional[str] = None

class ErrorResponse(BaseModel):
    error: dict  # Contains: code (str), message (str), details (dict, optional)
```

**Example Error Response**:
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

**Error Codes**:
- `VALIDATION_ERROR`: Request validation failed (422)
- `NOT_FOUND`: Resource not found (404)
- `BAD_REQUEST`: Malformed request (400)
- `INTERNAL_ERROR`: Unexpected server error (500)

## Entity Relationship Diagram

```
┌──────────────────┐
│  AccountType     │ (reference data)
│  ─────────────   │
│  account_type_id │
│  type_name       │
│  is_asset        │
└────────┬─────────┘
         │
         │ 1:N
         │
┌────────▼─────────┐       ┌────────────────┐
│     Account      │       │    Currency    │ (reference data)
│  ─────────────   │       │  ────────────  │
│  account_id      │◄──────┤  currency_code │
│  account_name    │  N:1  │  currency_name │
│  current_balance │       └────────────────┘
└────────┬─────────┘
         │
         │ 1:N
         │
┌────────▼──────────────┐       ┌────────────────┐
│    Transaction        │       │    Category    │
│  ──────────────────   │  N:1  │  ────────────  │
│  transaction_id       ├───────►  category_id   │
│  amount               │       │  category_name │
│  transaction_type     │       │  category_type │
│  transaction_date     │       └────────────────┘
└───────────┬───────────┘
            │
            │ N:1
            │
       ┌────▼────────┐
       │   Payee     │
       │  ─────────  │
       │  payee_id   │
       │  payee_name │
       └─────────────┘
```

**Relationships Summary**:
- Account → AccountType (many-to-one, required)
- Account → Currency (many-to-one, required)
- Transaction → Account (many-to-one, required)
- Transaction → Category (many-to-one, optional)
- Transaction → Payee (many-to-one, optional)
- Transaction → Currency (many-to-one, required)
- Payee → Category (many-to-one, optional, for default category)

## Validation Summary

All validation rules from functional requirements mapped to Pydantic field validators:

| Rule | Field | Validation | Database Constraint |
|------|-------|------------|---------------------|
| FR-009 | Transaction.amount | `Field(gt=0)` - must be positive | Amount > 0 (implicit) |
| FR-010 | Transaction.transaction_date | `date` type - ISO 8601 | DATE type |
| FR-011 | Transaction.transaction_type | `Literal["income", "expense"]` | CHECK constraint |
| FR-011 | Transaction.status | `Literal["pending", "cleared", "reconciled", "void"]` | CHECK constraint |
| FR-012 | Transaction.account_id | Database FK check in service layer | FOREIGN KEY constraint |
| FR-012 | Transaction.category_id | Database FK check in service layer | FOREIGN KEY constraint |
| FR-012 | Transaction.payee_id | Database FK check in service layer | FOREIGN KEY constraint |
| FR-021 | Account.account_type_id | Database FK check in service layer | FOREIGN KEY constraint |
| FR-022 | Account.currency_code | `Field(pattern=r"^[A-Z]{3}$")` | FOREIGN KEY constraint |
| FR-046 | All Create schemas | Pydantic required fields | NOT NULL constraints |
| FR-047 | All schemas | Pydantic type validation | Column types |

**Note**: Foreign key validation errors are caught at the database level and returned as 422 Unprocessable Entity with appropriate error messages.

## Index Summary

**Existing Indexes** (from migration files):

Transactions:
- `idx_account_date` on (account_id, transaction_date) - Fast filtering by account and date range
- `idx_category_date` on (category_id, transaction_date) - Fast filtering by category
- `idx_transaction_date` on (transaction_date) - Fast date range queries

Categories:
- `idx_category_type` on (category_type) - Fast filtering by type
- `idx_category_group` on (category_group) - Fast filtering by group

Payees:
- `idx_payee_name` on (payee_name) - Fast payee name searches

Accounts:
- `idx_accounts_opening_balance_date` on (opening_balance_date) - Balance date queries

These indexes support the query patterns required for list endpoints with filtering.

## Database Triggers & Automatic Maintenance

### Balance Management

**Trigger**: `account_balance_trigger` on transactions table

**Function**: `maintain_account_balance()`

**Behavior**:
- **INSERT**: Updates account current_balance based on transaction type
  - income: +amount
  - expense: -amount
  - transfer: -amount (source), +amount (destination)
- **UPDATE**: Calculates net change and adjusts balance
- **DELETE**: Reverses the transaction's impact on balance

**API Impact**: The API does NOT need to calculate or update account balances. The database handles this automatically.

### Timestamp Management

**Trigger**: `update_*_updated_at` on accounts, transactions, payees

**Function**: `update_updated_at_column()`

**Behavior**: Automatically sets `updated_at = CURRENT_TIMESTAMP` on UPDATE operations

**API Impact**: The API does NOT need to set updated_at timestamps.

## Out of Scope Elements

### Transfer Transactions

**Database Support**: The schema supports transfer transactions with `transfer_account_id`

**API Restriction**: This CRUD API does NOT support creating or managing transfer transactions:
- Only `income` and `expense` types allowed in create/update
- `transfer_account_id` field is read-only in responses
- Transfer logic requires additional business rules (out of scope)

**Rationale**: Transfer transactions involve two accounts and require coordinated updates. This adds complexity beyond simple CRUD operations. Will be addressed in a future feature.

### Transaction Splits

**Database Table**: `transaction_splits` table exists for splitting transactions across categories

**API Restriction**: Transaction splits are OUT OF SCOPE for this CRUD API

**Rationale**: Split transactions require additional endpoints and business logic beyond simple CRUD

### Exchange Rates

**Database Table**: `exchange_rates` table exists for currency conversion

**API Restriction**: Exchange rate management is OUT OF SCOPE

**Rationale**: Exchange rates require external data sources and scheduled updates. This API assumes exchange_rate=1.0 or manual entry

## Summary

This data model provides:

1. **Accurate Schema Mapping**: Direct mapping to existing PostgreSQL schema from migration files
2. **Complete Field Coverage**: All database fields exposed in API schemas
3. **Type Safety**: SQLAlchemy ORM + Pydantic validation ensure type-safe operations
4. **Proper Nullability**: Optional fields correctly marked based on database schema
5. **Database-Driven Logic**: Balance calculations and timestamps handled by database
6. **Clear Scope**: Transfer transactions and splits explicitly marked as out of scope
7. **Consistent Naming**: Uses database column names (transaction_id, account_id, etc.)

Ready to generate API contracts (OpenAPI specification) in next step.
