# AI Expense Tracker Service

REST API for expense tracking with CRUD operations for transactions, accounts, categories, and payees.

## Features

- **Transaction Management**: Create, retrieve, update, delete, and filter financial transactions
- **Account Management**: Manage financial accounts (checking, savings, credit cards, cash)
- **Category Management**: Organize expenses by categories
- **Payee Management**: Track merchants and vendors
- **Reference Data**: Access account types and currencies
- **Automatic Balance Calculation**: Database triggers maintain account balances automatically

## Tech Stack

- **Framework**: FastAPI (async web framework)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Database**: PostgreSQL 15+
- **Testing**: pytest with async support

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ with schema already created
- uv package manager (recommended) or pip

## Setup

1. **Clone the repository**
   ```bash
   cd ai-expense-tracker-service
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv pip install -e .
   uv pip install -e ".[dev]"

   # Or using pip
   pip install -e .
   pip install -e ".[dev]"
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Verify database migrations are applied**
   The PostgreSQL schema should already exist from `../ai-expense-tracker-agent/PostgreSQL-migrations/`

## Running the API

**Development server**:
```bash
uvicorn src.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs (Swagger): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

**Health check**:
```bash
curl http://localhost:8000/health
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI spec**: http://localhost:8000/openapi.json

## Project Structure

```
ai-expense-tracker-service/
├── src/
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic validation schemas
│   ├── routers/         # FastAPI route handlers
│   ├── services/        # Business logic (CRUD operations)
│   ├── config.py        # Configuration management
│   ├── database.py      # Database session management
│   └── main.py          # FastAPI application entry point
├── tests/
│   ├── unit/            # Unit tests for services
│   ├── integration/     # API integration tests
│   └── contract/        # OpenAPI contract tests
├── specs/               # Design documentation
├── pyproject.toml       # Project dependencies
└── .env.example         # Environment variables template
```

## Testing

**Run all tests**:
```bash
pytest
```

**Run with coverage**:
```bash
pytest --cov=src --cov-report=html
```

**Run specific test types**:
```bash
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest tests/contract/          # Contract tests only
```

## API Examples

### Create an Account
```bash
curl -X POST http://localhost:8000/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "account_name": "Chase Checking",
    "account_type_id": 1,
    "currency_code": "USD",
    "opening_balance": 1000.00
  }'
```

### Create a Transaction
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

### List Transactions with Filters
```bash
curl "http://localhost:8000/transactions?account_id=1&limit=10&start_date=2025-01-01"
```

### Get Account with Current Balance
```bash
curl http://localhost:8000/accounts/1
```

## Development Workflow

1. **Make changes** to code
2. **Run tests** to verify: `pytest`
3. **Check coverage**: `pytest --cov=src`
4. **Manual testing**: Use Swagger UI at /docs
5. **Commit changes** with clear messages

## Architecture

This API follows a three-layer architecture:

- **Routers** (`src/routers/`): Handle HTTP requests/responses, validation, status codes
- **Services** (`src/services/`): Contain business logic and CRUD operations
- **Models** (`src/models/`): SQLAlchemy ORM models mapping to database tables

Database triggers automatically maintain account balances when transactions are created, updated, or deleted.

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: development, staging, or production
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR
- `DB_POOL_SIZE`: Connection pool size (default: 20)
- `DB_MAX_OVERFLOW`: Max overflow connections (default: 30)

## Design Documentation

See `specs/001-crud-api/` for complete design documentation:
- `spec.md`: Feature specification and requirements
- `plan.md`: Implementation plan and architecture
- `data-model.md`: Data model and entity definitions
- `contracts/openapi.yaml`: OpenAPI 3.0 specification
- `tasks.md`: Implementation task breakdown

## License

[Add your license here]

## Support

For issues and questions, please refer to the project documentation in the `specs/` directory.
