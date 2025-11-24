# Technical Research: Table Names List Endpoint

**Feature**: 003-list-tables
**Date**: 2025-11-24
**Status**: Complete

## Overview

This document captures technical decisions for implementing a lightweight endpoint that returns a list of all table names from the PostgreSQL public schema.

## Key Technical Decisions

### Decision 1: Query Strategy

**Decision**: Query `information_schema.tables` WHERE `table_schema = 'public'` AND `table_type = 'BASE TABLE'`

**Rationale**:
- Standard SQL approach (portable, well-documented)
- Filters out views, materialized views, and system tables
- Consistent with existing schema discovery endpoints (feature 002)
- Simple query with minimal performance overhead

**Alternatives Considered**:
- **pg_catalog.pg_tables**: PostgreSQL-specific, less portable, no significant performance benefit
- **Query pg_class directly**: More complex, requires understanding PostgreSQL internals, harder to maintain
- **Include views**: Rejected - spec requires BASE TABLE only for consistency

**Best Practices**:
- Use parameterized queries (SQLAlchemy text() with bound parameters)
- Filter at database level, not application level
- Sort alphabetically in SQL (`ORDER BY table_name`) for efficiency

### Decision 2: Response Format

**Decision**: Return `List[str]` directly (no wrapper object)

**Rationale**:
- Minimal overhead - just an array of strings
- Easy to consume by clients (no nesting)
- Consistent with REST best practices for simple collections
- FastAPI automatically serializes to JSON array

**Alternatives Considered**:
- **Wrapper object** (e.g., `{"tables": [...]})`): Adds unnecessary nesting for simple data
- **Object array** (e.g., `[{"name": "..."}]`): More verbose, no additional value
- **Dictionary keyed by name**: Not ordered, less intuitive for iteration

**OpenAPI Schema**:
```yaml
responses:
  200:
    description: List of table names
    content:
      application/json:
        schema:
          type: array
          items:
            type: string
          example: ["accounts", "categories", "currencies", "transactions"]
```

### Decision 3: Service Layer Function

**Decision**: Add `get_table_names(db: Session) -> List[str]` to existing `schema_service.py`

**Rationale**:
- Follows established pattern from feature 002
- Keeps all schema discovery logic in one service module
- Reuses existing database session management
- Single responsibility: query information_schema and return names

**Implementation Pattern**:
```python
def get_table_names(db: Session) -> List[str]:
    """
    Retrieve all table names from the public schema.

    Args:
        db: Database session

    Returns:
        List of table names sorted alphabetically
    """
    query = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)

    result = db.execute(query)
    table_names = [row.table_name for row in result]
    logger.info(f"Retrieved {len(table_names)} table names")
    return table_names
```

**Best Practices**:
- Log the count of tables retrieved for monitoring
- Use list comprehension for clean result extraction
- Let SQLAlchemy handle connection/transaction management
- Return empty list (not None) when no tables exist

### Decision 4: Router Endpoint Design

**Decision**: Add `GET /schema/tables` endpoint to existing schema router

**Rationale**:
- RESTful path: `/schema/tables` lists tables, `/schema/tables/{name}` gets details
- Keeps all schema discovery under `/schema` prefix
- Consistent with existing endpoint structure
- No path conflicts with existing `/schema/tables/{table_name}` endpoint

**Error Handling**:
- 200 OK: Success (even if empty array)
- 500 Internal Server Error: Database connection failures, query errors

**Endpoint Signature**:
```python
@router.get(
    "/tables",
    response_model=List[str],
    summary="Get all table names",
    tags=["schema"]
)
def get_table_names_endpoint(db: Session = Depends(get_db)):
    """Get list of all table names from the public schema."""
```

### Decision 5: Testing Strategy

**Decision**: Three-layer testing approach

**Test Layers**:

1. **Unit Tests** (`tests/unit/test_schema_service.py`):
   - Test `get_table_names()` function directly
   - Verify correct SQL query execution
   - Verify alphabetical sorting
   - Verify empty list when no tables

2. **Integration Tests** (`tests/integration/test_schema_api.py`):
   - Test endpoint with TestClient
   - Verify 200 response with correct content type
   - Verify actual table names from database
   - Verify response matches known schema
   - Test database error scenarios

3. **Contract Tests** (OpenAPI validation):
   - Verify response matches OpenAPI schema
   - Verify endpoint appears in /docs

**Best Practices**:
- Use existing test fixtures for database sessions
- Test with real database (not mocks) for integration tests
- Assert exact table names match expected production schema
- Test performance (<100ms target)

## Performance Considerations

**Query Performance**:
- `information_schema.tables` is a view, but query is simple (no joins needed for this endpoint)
- Filter by schema and table_type reduces result set immediately
- ORDER BY on small result set (<100 tables expected) is negligible
- Expected query time: <10ms

**Caching Strategy**:
- Not needed for MVP - schema changes are infrequent
- If needed later, can add application-level caching with TTL
- Cache invalidation would be manual (after schema migrations)

**Benchmarks**:
- Target: <100ms end-to-end (well below existing schema endpoints)
- Query: <10ms
- JSON serialization: <1ms (small string array)
- Network overhead: <90ms

## Security Considerations

**SQL Injection**:
- Use SQLAlchemy `text()` with parameterized queries (though no user input in this query)
- Hard-coded schema filter (`table_schema = 'public'`) prevents schema traversal

**Information Disclosure**:
- Only public schema exposed (no system tables, no other schemas)
- Table names alone don't reveal sensitive data
- Follows same security model as existing schema endpoints

**Access Control**:
- Endpoint inherits authentication/authorization from schema router
- No additional permissions needed (read-only metadata)

## Dependencies

**No New Dependencies**:
- Uses existing FastAPI, SQLAlchemy, Pydantic stack
- No additional packages required

**Existing Dependencies Used**:
- FastAPI 0.121.2: Router, dependency injection, OpenAPI
- SQLAlchemy 2.0.44: Database queries, session management
- Python 3.11: Type hints (List[str])

## Migration Considerations

**No Schema Changes Required**:
- Read-only query to existing information_schema
- No database migrations needed
- No new tables or columns

## Monitoring & Observability

**Logging**:
- Log requests to endpoint (existing middleware)
- Log result count: `logger.info(f"Retrieved {len(table_names)} table names")`
- Log errors: Database failures, unexpected exceptions

**Metrics** (existing infrastructure):
- Request count
- Response time (p50, p95, p99)
- Error rate
- Success rate

## Open Questions & Assumptions

**Assumptions**:
- Public schema contains production tables (verified in feature 002)
- Table count is reasonable (<100 tables, typical for this domain)
- Schema changes are infrequent (no caching needed)
- Clients need alphabetically sorted results

**No Open Questions**:
All requirements are clear and implementation is straightforward.

## References

- Feature 002 (Database Schema Discovery API): Established patterns for schema endpoints
- PostgreSQL information_schema documentation: Standard SQL views
- FastAPI documentation: List[str] response models
- Existing codebase: `src/services/schema_service.py`, `src/routers/schema.py`
