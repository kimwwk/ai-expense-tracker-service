# Research & Technology Decisions

**Feature**: Basic CRUD REST API for Expense Tracking
**Date**: 2025-11-16
**Phase**: 0 (Outline & Research)

## Overview

This document captures research findings and technology decisions for building a lightweight REST API service for expense tracking. The service provides CRUD operations over PostgreSQL with minimal business logic (database handles calculations via triggers).

## Technology Stack Decisions

### 1. Web Framework: FastAPI

**Decision**: Use FastAPI as the web framework

**Rationale**:
- **Automatic API Documentation**: FastAPI generates OpenAPI (Swagger) and ReDoc documentation automatically from code, eliminating manual API spec maintenance
- **Built-in Validation**: Native integration with Pydantic provides request/response validation with minimal boilerplate
- **High Performance**: Built on Starlette and Pydantic, FastAPI offers performance comparable to NodeJS and Go frameworks
- **Async Support**: Native async/await support enables efficient handling of I/O-bound operations (database queries)
- **Type Safety**: Leverages Python type hints for IDE autocomplete, static analysis, and runtime validation
- **Industry Adoption**: Widely used in production (Microsoft, Netflix, Uber) with strong community support

**Alternatives Considered**:
1. **Flask**: Rejected because it lacks async support, requires additional libraries for validation (marshmallow) and API documentation (flasgger), and has more boilerplate for REST APIs
2. **Django REST Framework**: Rejected because Django is heavyweight for a simple CRUD API, includes ORM abstractions we don't need (we have existing schema), and has slower performance than FastAPI
3. **Raw ASGI (Starlette)**: Rejected because we'd need to build validation, serialization, and documentation ourselves - reinventing what FastAPI provides

### 2. Database ORM: SQLAlchemy

**Decision**: Use SQLAlchemy Core + ORM for database access

**Rationale**:
- **Type Safety**: ORM models provide type-safe database access with IDE support
- **Connection Pooling**: Built-in connection pool management reduces connection overhead
- **SQL Injection Prevention**: Parameterized queries prevent SQL injection attacks
- **Database Agnostic**: While we use PostgreSQL, SQLAlchemy abstracts dialect differences
- **Query Building**: Pythonic query construction reduces raw SQL string manipulation errors
- **Integration with FastAPI**: Standard dependency injection pattern for database sessions

**Alternatives Considered**:
1. **Raw psycopg2**: Rejected because writing raw SQL for 50+ endpoints is error-prone, lacks type safety, and requires manual connection pooling
2. **SQLModel**: Rejected because it's less mature than SQLAlchemy, has smaller ecosystem, and doesn't offer significant advantages for our use case
3. **Databases (encode)**: Rejected because it's async-only with limited ORM features, requiring more manual query building

**Implementation Notes**:
- Use SQLAlchemy ORM models to map to existing PostgreSQL schema
- Leverage database session dependency injection in FastAPI
- Let database triggers handle account balance calculations (per spec requirement)

### 3. Validation: Pydantic

**Decision**: Use Pydantic v2 for request/response validation and serialization

**Rationale**:
- **Native FastAPI Integration**: FastAPI uses Pydantic internally, making it the natural choice
- **Performance**: Pydantic v2 (Rust core) offers 5-10x performance improvement over v1
- **Validation Rules**: Supports complex validation (regex, ranges, custom validators) out of the box
- **JSON Schema**: Automatically generates JSON schema for API documentation
- **Type Safety**: Full type hint support with mypy compatibility

**Alternatives Considered**:
1. **Marshmallow**: Rejected because it's not natively integrated with FastAPI, has slower performance, and requires more boilerplate
2. **Manual Validation**: Rejected because writing validation for 50+ endpoints is tedious and error-prone

**Implementation Notes**:
- Create separate schemas for Create, Update, and Response operations per resource
- Use Pydantic's Field() for validation constraints (min/max, regex patterns)
- Leverage Config class for ORM mode (automatic conversion from SQLAlchemy models)

### 4. Testing Framework: pytest

**Decision**: Use pytest with pytest-asyncio and httpx for testing

**Rationale**:
- **Better Ergonomics**: Fixtures, parametrization, and assertion introspection superior to unittest
- **Async Support**: pytest-asyncio enables testing of async FastAPI endpoints
- **Rich Ecosystem**: Extensive plugin ecosystem (coverage, mock, fixtures)
- **FastAPI TestClient**: httpx provides async test client that integrates seamlessly with FastAPI

**Alternatives Considered**:
1. **unittest**: Rejected because it has verbose syntax, lacks fixtures, and requires more boilerplate
2. **nose2**: Rejected because pytest has better maintenance and larger community

**Implementation Notes**:
- Unit tests for service layer functions (validation logic, data transformations)
- Integration tests using FastAPI TestClient (full request/response cycle)
- Contract tests validating OpenAPI schema compliance
- Use pytest fixtures for database setup/teardown (transaction rollback per test)

### 5. Database Driver: psycopg2

**Decision**: Use psycopg2 (binary) as PostgreSQL adapter

**Rationale**:
- **Mature & Stable**: Battle-tested driver with 15+ years of production use
- **SQLAlchemy Support**: Recommended driver for SQLAlchemy with PostgreSQL
- **Performance**: Compiled C extension provides better performance than pure Python
- **Feature Complete**: Supports all PostgreSQL features we need (prepared statements, connection pooling)

**Alternatives Considered**:
1. **asyncpg**: Rejected because we're using SQLAlchemy which handles async at the ORM level, and asyncpg requires different query patterns
2. **psycopg3**: Rejected because it's newer and less battle-tested; psycopg2 is sufficient for our needs

**Implementation Notes**:
- Install psycopg2-binary for easier deployment (includes compiled libraries)
- Configure connection pool in SQLAlchemy (pool_size=20, max_overflow=30)

### 6. ASGI Server: Uvicorn

**Decision**: Use Uvicorn as the ASGI application server

**Rationale**:
- **FastAPI Recommendation**: Official ASGI server recommended by FastAPI documentation
- **Performance**: Built on uvloop and httptools for high performance
- **Production Ready**: Used in production by many companies
- **Simple Configuration**: Minimal configuration needed for basic deployment

**Alternatives Considered**:
1. **Hypercorn**: Rejected because Uvicorn has better performance benchmarks and larger community
2. **Daphne**: Rejected because it's Django-focused and slower than Uvicorn

**Implementation Notes**:
- Use uvicorn with --workers flag for production (one worker per CPU core)
- Configure logging to JSON format for structured logs

## Best Practices & Patterns

### REST API Design Patterns

**Decision**: Follow standard REST conventions from the specification

**Key Patterns**:
1. **Resource-Based URLs**: `/transactions`, `/accounts`, `/categories`, `/payees`
2. **HTTP Method Semantics**:
   - POST for create (201 Created with Location header)
   - GET for read (200 OK)
   - PUT for full update (200 OK or 204 No Content)
   - PATCH for partial update (200 OK or 204 No Content)
   - DELETE for remove (204 No Content)
3. **Error Response Format**: Consistent JSON structure with error code, message, and optional details
4. **Pagination**: Query parameters (limit, offset) with metadata in response
5. **Filtering**: Query parameters for resource-specific filters
6. **Sorting**: Query parameters (sort, order)

**Rationale**: These are industry-standard REST patterns that provide predictable, discoverable APIs

### Project Structure Pattern

**Decision**: Three-layer architecture (routers → services → models)

**Layer Responsibilities**:
1. **Models** (SQLAlchemy ORM):
   - Map to database tables
   - Define relationships
   - No business logic
2. **Schemas** (Pydantic):
   - Request/response validation
   - Serialization
   - No database knowledge
3. **Services** (Business Logic):
   - CRUD operations
   - Query building
   - Validation orchestration
   - No HTTP knowledge
4. **Routers** (HTTP Handlers):
   - HTTP request/response handling
   - Status codes
   - Dependency injection
   - No business logic

**Rationale**: Clear separation of concerns makes testing easier and code more maintainable. Each layer has a single responsibility.

### Database Session Management

**Decision**: Use FastAPI dependency injection for database sessions

**Pattern**:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/transactions")
def list_transactions(db: Session = Depends(get_db)):
    # Use db here
```

**Rationale**: FastAPI's dependency injection ensures:
- Sessions are created per request
- Sessions are always closed (even on exceptions)
- Sessions can be easily mocked in tests

### Error Handling Pattern

**Decision**: Use FastAPI exception handlers with custom exception classes

**Pattern**:
```python
class NotFoundException(Exception):
    pass

@app.exception_handler(NotFoundException)
def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "NOT_FOUND", "message": str(exc)}}
    )
```

**Rationale**: Centralized error handling ensures consistent error responses across all endpoints

## Configuration & Environment

### Environment Variables

**Decision**: Use environment variables for configuration with sensible defaults

**Required Variables**:
- `DATABASE_URL`: PostgreSQL connection string (format: `postgresql://user:pass@host:port/dbname`)
- `ENVIRONMENT`: Deployment environment (development, staging, production)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

**Optional Variables**:
- `DB_POOL_SIZE`: Connection pool size (default: 20)
- `DB_MAX_OVERFLOW`: Max overflow connections (default: 30)
- `CORS_ORIGINS`: Allowed CORS origins (default: *)

**Rationale**: 12-factor app principles - configuration via environment enables deployment flexibility

### Logging Strategy

**Decision**: Structured JSON logging with log levels

**Implementation**:
- Use Python's standard logging module
- JSON format for production (easier parsing)
- Human-readable format for development
- Log levels: DEBUG (development), INFO (production), ERROR (alerts)

**What to Log**:
- Request path, method, status code, duration (INFO)
- Database queries >500ms (WARNING)
- Validation errors with field details (WARNING)
- Unhandled exceptions with stack traces (ERROR)
- Health check requests (DEBUG)

**Rationale**: Structured logs enable easy querying and analysis in log aggregation systems

## Development Workflow

### Dependency Management

**Decision**: Use `uv` for Python dependency management (per project standard)

**Rationale**:
- Project uses `uv` over `pip` (documented in CLAUDE.md)
- Faster than pip
- Better dependency resolution

**Implementation**:
- `pyproject.toml` defines dependencies
- `uv pip install` for installation
- `uv pip compile` for lock file generation

### Testing Approach

**Decision**: Test pyramid with emphasis on integration tests

**Test Distribution**:
- **Unit Tests (30%)**: Service layer validation logic, data transformations
- **Integration Tests (60%)**: Full API endpoint tests with test database
- **Contract Tests (10%)**: OpenAPI schema validation

**Rationale**: Integration tests provide best ROI for REST APIs - they verify end-to-end behavior including routing, validation, database access, and serialization

### Database Schema Assumption

**Decision**: Assume existing PostgreSQL schema with tables, constraints, and triggers

**Assumption Details** (from spec):
- Tables: transactions, accounts, categories, payees, account_types, currencies
- Foreign key constraints enforce referential integrity
- Database triggers maintain account balances
- created_at, updated_at timestamps managed by database

**Rationale**: Spec explicitly states "Database Schema Exists" as assumption. We focus on API layer, not schema creation.

## Performance Considerations

### Query Optimization

**Strategies**:
1. **Pagination Defaults**: Limit=50 (default), max=100 prevents unbounded queries
2. **Index Assumptions**: Assume existing schema has proper indexes on foreign keys and commonly filtered columns
3. **Query Timeout**: Set PostgreSQL statement_timeout=30s to prevent runaway queries
4. **Connection Pooling**: Reuse connections via SQLAlchemy pool (pool_size=20, max_overflow=30)

**Rationale**: These strategies keep query performance within target latency (<200ms simple, <1s filtered lists)

### Memory Management

**Strategies**:
1. **Streaming Results**: Use SQLAlchemy's streaming for large result sets (though pagination limits this)
2. **Connection Pool Size**: Limit concurrent connections to prevent memory exhaustion
3. **No Result Caching**: Keep it simple initially (spec assumes no caching)

**Rationale**: Memory target is <500MB per instance - connection pooling and pagination keep us within budget

## Security Considerations

### SQL Injection Prevention

**Strategy**: Use SQLAlchemy ORM and parameterized queries exclusively

**Rationale**: ORM prevents SQL injection by design. Never concatenate user input into SQL strings.

### Input Validation

**Strategy**: Pydantic validates all inputs before they reach business logic

**Validation Rules** (per spec):
- Amount: Positive decimal (FR-009)
- Dates: ISO 8601 format (FR-010)
- Enums: Allowed values only (FR-011)
- Foreign Keys: Reference existing records (FR-012)
- Currency: 3-letter ISO code (FR-022)

**Rationale**: Input validation at API boundary prevents invalid data from reaching database

### No Authentication in This Feature

**Note**: Per spec assumption #2, this API does not implement authentication or multi-tenancy. All resources are accessible to any client. User/tenant isolation will be added in a future feature.

**Rationale**: Keeping scope focused on basic CRUD operations per spec requirements

## Deployment Considerations

### Containerization

**Decision**: Use Docker for containerized deployment

**Rationale**:
- Consistent environment across development and production
- Easy deployment to container orchestration platforms (Kubernetes, ECS)
- Simplifies dependency management

**Implementation**:
- Multi-stage Dockerfile (builder + runtime)
- Base image: python:3.11-slim
- Non-root user for security

### Health Checks

**Decision**: Implement `/health` endpoint for monitoring

**Health Check Logic**:
- Database connectivity test
- Return 200 OK if healthy, 503 Service Unavailable if unhealthy

**Rationale**: Container orchestrators and load balancers need health checks for zero-downtime deployments

## Open Questions & Future Considerations

### Questions Resolved

1. ~~Which Python version?~~ → Python 3.11 or 3.12 (both supported by dependencies)
2. ~~Async vs sync routes?~~ → Async routes (FastAPI async support, better for I/O-bound operations)
3. ~~How to handle database migrations?~~ → Not in scope (spec assumes existing schema)
4. ~~Need API versioning?~~ → Not initially (single version API, can add `/v1` prefix later if needed)

### Future Enhancements (Out of Scope for This Feature)

1. **Authentication & Authorization**: JWT tokens, role-based access control
2. **Multi-tenancy**: Tenant isolation, user-specific data filtering
3. **Caching Layer**: Redis for frequently accessed data (accounts, reference data)
4. **Rate Limiting**: Protect API from abuse
5. **API Versioning**: URL-based versioning (/v1, /v2) as API evolves
6. **Database Migrations**: Alembic for schema version management
7. **Observability**: Distributed tracing (OpenTelemetry), metrics (Prometheus)

**Rationale**: These are valuable but add complexity. Spec principles favor boring, simple solutions. Add complexity only when needed.

## Summary

All technology decisions prioritize:
1. **Simplicity**: Standard patterns, minimal abstractions
2. **Type Safety**: Leveraging Python type hints throughout
3. **Testing**: Easy to test with clear layer boundaries
4. **Performance**: Meeting latency targets without premature optimization
5. **Maintainability**: Boring, obvious code over clever tricks

No unresolved questions remain. Ready to proceed to Phase 1 (Design & Contracts).
