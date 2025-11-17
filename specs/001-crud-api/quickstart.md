# Quick Start Guide

**Feature**: Basic CRUD REST API for Expense Tracking
**Date**: 2025-11-16
**Audience**: Developers implementing this feature

## Overview

This guide provides step-by-step instructions to implement the expense tracking REST API. The implementation follows the design artifacts in this feature directory:

- [spec.md](spec.md) - Feature specification and requirements
- [plan.md](plan.md) - Implementation plan and technical decisions
- [research.md](research.md) - Technology research and best practices
- [data-model.md](data-model.md) - Data model and schema definitions
- [contracts/openapi.yaml](contracts/openapi.yaml) - OpenAPI 3.0 API specification

## Prerequisites

Before starting implementation:

1. **Python 3.11+** installed (`python --version`)
2. **uv** package manager installed (per project standard)
3. **PostgreSQL 15+** running with schema already created
4. **Database migrations** applied from `../ai-expense-tracker-agent/PostgreSQL-migrations/`
5. **Git** repository initialized and on branch `001-crud-api`

## Implementation Roadmap

### Phase 1: Project Setup (30 minutes)

**Goal**: Initialize Python project structure and dependencies

**Steps**:

1. **Create project structure**:
   ```bash
   mkdir -p src/{models,schemas,routers,services}
   mkdir -p tests/{unit,integration,contract}
   touch src/__init__.py
   touch src/{models,schemas,routers,services}/__init__.py
   touch tests/__init__.py
   touch tests/{unit,integration,contract}/__init__.py
   ```

2. **Create `pyproject.toml`** with dependencies:
   ```toml
   [project]
   name = "ai-expense-tracker-service"
   version = "1.0.0"
   description = "REST API for expense tracking"
   requires-python = ">=3.11"
   dependencies = [
       "fastapi>=0.104.0",
       "uvicorn[standard]>=0.24.0",
       "sqlalchemy>=2.0.0",
       "psycopg2-binary>=2.9.9",
       "pydantic>=2.5.0",
       "python-dotenv>=1.0.0",
   ]

   [project.optional-dependencies]
   dev = [
       "pytest>=7.4.0",
       "pytest-asyncio>=0.21.0",
       "httpx>=0.25.0",
       "pytest-cov>=4.1.0",
   ]
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -e .
   uv pip install -e ".[dev]"
   ```

4. **Create `.env.example`**:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/expense_tracker
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   DB_POOL_SIZE=20
   DB_MAX_OVERFLOW=30
   ```

5. **Copy and configure `.env`**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual database credentials
   ```

**Validation**: Run `python -c "import fastapi; import sqlalchemy; print('Dependencies OK')"`

### Phase 2: Core Infrastructure (1 hour)

**Goal**: Set up configuration, database connection, and logging

**Files to create**:

1. **src/config.py** - Configuration management
   ```python
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       database_url: str
       environment: str = "development"
       log_level: str = "INFO"
       db_pool_size: int = 20
       db_max_overflow: int = 30

       class Config:
           env_file = ".env"

   settings = Settings()
   ```

2. **src/database.py** - Database session management
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker, declarative_base
   from src.config import settings

   engine = create_engine(
       settings.database_url,
       pool_size=settings.db_pool_size,
       max_overflow=settings.db_max_overflow,
   )

   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   Base = declarative_base()

   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

3. **src/main.py** - FastAPI application entry point
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   app = FastAPI(
       title="AI Expense Tracker Service API",
       description="REST API for expense tracking",
       version="1.0.0",
   )

   # CORS middleware (configure as needed)
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Configure for production
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   @app.get("/health")
   def health_check():
       return {"status": "healthy"}
   ```

**Validation**: Run `uvicorn src.main:app --reload` and access http://localhost:8000/health

### Phase 3: SQLAlchemy Models (2 hours)

**Goal**: Create ORM models mapping to database tables

**Reference**: [data-model.md](data-model.md) for complete model definitions

**Files to create** (in `src/models/`):

1. **currency.py** - Currency reference data model
2. **account_type.py** - Account type reference data model
3. **account.py** - Account model with relationships
4. **category.py** - Category model
5. **payee.py** - Payee model with default_category relationship
6. **transaction.py** - Transaction model with all relationships

**Key Implementation Notes**:
- Use `Mapped[type]` type hints for all columns
- Set `__tablename__` to match database table names
- Use exact column names from schema (e.g., `transaction_id`, `account_id`)
- Define foreign key relationships with `ForeignKey()` and `relationship()`
- Set `server_default` for timestamps (database manages these)
- Mark nullable fields with `Optional[type]`

**Validation**:
```python
# Test imports
from src.models.transaction import Transaction
from src.models.account import Account
print("Models imported successfully")
```

### Phase 4: Pydantic Schemas (2 hours)

**Goal**: Create request/response validation schemas

**Reference**: [data-model.md](data-model.md) for schema definitions

**Files to create** (in `src/schemas/`):

1. **enums.py** - Enum definitions (TransactionType, TransactionStatus, CategoryType)
2. **common.py** - Common schemas (PaginationMetadata, PaginatedResponse, ErrorResponse)
3. **transaction.py** - TransactionCreate, TransactionUpdate, TransactionResponse
4. **account.py** - AccountCreate, AccountUpdate, AccountResponse
5. **category.py** - CategoryCreate, CategoryUpdate, CategoryResponse
6. **payee.py** - PayeeCreate, PayeeUpdate, PayeeResponse

**Key Implementation Notes**:
- Use `Field()` for validation constraints (min_length, max_length, pattern, gt)
- Use `Literal[]` for enum validation
- Set `model_config = ConfigDict(from_attributes=True)` for response schemas
- Mark optional fields with `Optional[type] = None`
- Use `default` parameter for fields with default values

**Validation**:
```python
from src.schemas.transaction import TransactionCreate
data = {
    "account_id": 1,
    "transaction_type": "expense",
    "amount": "50.00",
    "currency_code": "USD",
    "base_amount": "50.00",
    "transaction_date": "2025-01-15"
}
txn = TransactionCreate(**data)
print(f"Validation passed: {txn}")
```

### Phase 5: Service Layer (3 hours)

**Goal**: Implement business logic and CRUD operations

**Files to create** (in `src/services/`):

1. **transaction_service.py** - Transaction CRUD + filtering/pagination
2. **account_service.py** - Account CRUD + filtering/pagination
3. **category_service.py** - Category CRUD + filtering/pagination
4. **payee_service.py** - Payee CRUD + filtering/pagination

**Service Function Pattern**:
```python
from sqlalchemy.orm import Session
from src.models.transaction import Transaction
from src.schemas.transaction import TransactionCreate, TransactionUpdate

def create_transaction(db: Session, data: TransactionCreate) -> Transaction:
    """Create a new transaction"""
    db_transaction = Transaction(**data.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction(db: Session, transaction_id: int) -> Transaction | None:
    """Get transaction by ID"""
    return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

def list_transactions(
    db: Session,
    account_id: int | None = None,
    category_id: int | None = None,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[Transaction], int]:
    """List transactions with filters and pagination"""
    query = db.query(Transaction)

    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    total = query.count()
    transactions = query.order_by(Transaction.transaction_id.desc()).limit(limit).offset(offset).all()

    return transactions, total

# Similar functions for update, patch, delete
```

**Key Implementation Notes**:
- All functions take `db: Session` as first parameter
- Return ORM models (not Pydantic schemas) - router handles conversion
- List functions return tuple: `(items: list, total: int)` for pagination
- Use `model_dump()` to convert Pydantic → dict for ORM
- Handle foreign key violations in router layer (catch IntegrityError)

**Validation**: Write unit tests for each service function

### Phase 6: API Routers (3 hours)

**Goal**: Create FastAPI route handlers

**Reference**: [contracts/openapi.yaml](contracts/openapi.yaml) for API specification

**Files to create** (in `src/routers/`):

1. **transactions.py** - Transaction endpoints
2. **accounts.py** - Account endpoints
3. **categories.py** - Category endpoints
4. **payees.py** - Payee endpoints
5. **reference.py** - Reference data endpoints (account types, currencies)

**Router Pattern**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from src.schemas.common import PaginatedResponse, PaginationMetadata
from src.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction"""
    try:
        transaction = transaction_service.create_transaction(db, data)
        return transaction
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Foreign key constraint failed",
                    "details": {"reason": str(e)}
                }
            }
        )

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get transaction by ID"""
    transaction = transaction_service.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Transaction with ID {transaction_id} not found"
                }
            }
        )
    return transaction

@router.get("", response_model=PaginatedResponse[TransactionResponse])
def list_transactions(
    account_id: int | None = None,
    category_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List transactions with filtering and pagination"""
    transactions, total = transaction_service.list_transactions(
        db, account_id=account_id, category_id=category_id, limit=limit, offset=offset
    )
    return {
        "data": transactions,
        "pagination": PaginationMetadata(limit=limit, offset=offset, total=total)
    }

# Similar patterns for PUT, PATCH, DELETE
```

**Register routers in src/main.py**:
```python
from src.routers import transactions, accounts, categories, payees, reference

app.include_router(transactions.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(payees.router)
app.include_router(reference.router)
```

**Key Implementation Notes**:
- Use `HTTPException` with detailed error structure matching OpenAPI spec
- Catch `IntegrityError` from SQLAlchemy for foreign key violations
- Set proper HTTP status codes (201 for create, 204 for delete, etc.)
- Use `response_model` parameter for automatic serialization
- Add Location header for 201 responses (FastAPI handles this with proper return)

**Validation**: Access http://localhost:8000/docs for auto-generated API documentation

### Phase 7: Testing (4 hours)

**Goal**: Write comprehensive tests

**Files to create** (in `tests/`):

1. **conftest.py** - Shared pytest fixtures
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   from src.main import app
   from src.database import Base, get_db

   TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/expense_tracker_test"

   @pytest.fixture(scope="function")
   def db_session():
       engine = create_engine(TEST_DATABASE_URL)
       Base.metadata.create_all(bind=engine)
       TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
       db = TestingSessionLocal()
       try:
           yield db
       finally:
           db.rollback()
           db.close()
           Base.metadata.drop_all(bind=engine)

   @pytest.fixture
   def client(db_session):
       def override_get_db():
           try:
               yield db_session
           finally:
               pass
       app.dependency_overrides[get_db] = override_get_db
       return TestClient(app)
   ```

2. **Unit tests** (tests/unit/test_*_service.py) - Test service functions
3. **Integration tests** (tests/integration/test_*_api.py) - Test API endpoints end-to-end
4. **Contract tests** (tests/contract/test_openapi_compliance.py) - Validate against OpenAPI spec

**Test Coverage Goals**:
- Unit tests: All service functions
- Integration tests: All API endpoints (happy path + error cases)
- Contract tests: Response format matches OpenAPI schema

**Run tests**:
```bash
pytest -v
pytest --cov=src --cov-report=html
```

### Phase 8: Documentation & Deployment (1 hour)

**Goal**: Final polish and deployment preparation

**Tasks**:

1. **Create README.md** with:
   - Project description
   - Setup instructions
   - API documentation link
   - Environment variables
   - Running locally
   - Running tests

2. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY pyproject.toml .
   RUN pip install -e .

   COPY src/ src/

   EXPOSE 8000

   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Test deployment**:
   ```bash
   docker build -t expense-tracker-api .
   docker run -p 8000:8000 --env-file .env expense-tracker-api
   ```

## Implementation Checklist

Track progress using this checklist:

- [ ] Phase 1: Project setup complete
- [ ] Phase 2: Core infrastructure working (health check accessible)
- [ ] Phase 3: All SQLAlchemy models created
- [ ] Phase 4: All Pydantic schemas created and validated
- [ ] Phase 5: All service functions implemented
- [ ] Phase 6: All API routers implemented
- [ ] Phase 7: Tests written and passing (target: >80% coverage)
- [ ] Phase 8: Documentation complete and Docker image builds

## Common Issues & Solutions

### Issue: Import errors with circular dependencies

**Solution**: Avoid importing models in `__init__.py`. Import models directly where needed.

### Issue: Foreign key violations not caught

**Solution**: Wrap database operations in try/except for `sqlalchemy.exc.IntegrityError`

### Issue: Pagination total count slow

**Solution**: Use `query.count()` instead of `len(query.all())` for efficiency

### Issue: Database triggers not firing

**Solution**: Verify migrations applied:
```bash
psql -d expense_tracker -f ../ai-expense-tracker-agent/PostgreSQL-migrations/20250818-02-balance-triggers.sql
```

### Issue: OpenAPI docs not showing all endpoints

**Solution**: Verify routers registered in `main.py` with `app.include_router()`

## API Testing Examples

### Create a transaction:
```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "transaction_type": "expense",
    "amount": 50.00,
    "currency_code": "USD",
    "base_amount": 50.00,
    "transaction_date": "2025-01-15",
    "description": "Grocery shopping"
  }'
```

### List transactions:
```bash
curl http://localhost:8000/transactions?account_id=1&limit=10
```

### Get account with current balance:
```bash
curl http://localhost:8000/accounts/1
```

## Next Steps

After completing this feature:

1. Run `/speckit.tasks` to generate implementation task breakdown
2. Review tasks.md for dependency-ordered implementation steps
3. Use `/speckit.implement` to execute tasks systematically
4. Create PR and request code review

## Support Resources

- **Feature Spec**: [spec.md](spec.md) - Requirements and acceptance criteria
- **Technical Plan**: [plan.md](plan.md) - Architecture and design decisions
- **Data Model**: [data-model.md](data-model.md) - Complete schema documentation
- **API Contract**: [contracts/openapi.yaml](contracts/openapi.yaml) - OpenAPI specification
- **Database Schema**: `../ai-expense-tracker-agent/PostgreSQL-migrations/` - Database migrations
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/en/20/
- **Pydantic Docs**: https://docs.pydantic.dev/latest/

Happy coding! 🚀
