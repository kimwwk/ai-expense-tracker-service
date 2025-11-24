# Research: Database Schema Discovery API

**Feature**: 002-database-schema-api
**Date**: 2025-11-23
**Purpose**: Document technical decisions and best practices for implementing schema discovery endpoints

## Overview

This document captures research findings and technical decisions for implementing a REST API that exposes PostgreSQL database schema information. The feature enables developers and AI agents to programmatically discover tables, columns, constraints, relationships, and reference data.

## Key Technical Decisions

### Decision 1: Schema Introspection Approach

**Decision**: Query PostgreSQL's `information_schema` views directly using raw SQL

**Rationale**:
- `information_schema` is a SQL standard (ANSI/ISO) supported by PostgreSQL
- Provides comprehensive metadata about tables, columns, constraints, and relationships
- Always reflects current database state without requiring manual updates
- Well-documented and battle-tested approach
- No need for SQLAlchemy reflection (which would add complexity)

**Alternatives Considered**:
1. **SQLAlchemy Metadata Reflection** - Rejected because:
   - Adds abstraction layer we don't need
   - Less control over exact data returned
   - Slower than direct SQL queries
   - Requires ORM model definitions (we're querying metadata, not tables)

2. **PostgreSQL System Catalogs (pg_catalog)** - Rejected because:
   - PostgreSQL-specific (less portable)
   - More complex queries required
   - information_schema provides cleaner abstraction
   - No significant performance benefit for our use case

**Implementation Notes**:
- Use `table_schema = 'public'` to filter out system tables
- Join `information_schema.columns` for column details
- Join `information_schema.table_constraints` and `key_column_usage` for constraints
- Use prepared statements with parameterized queries for security

### Decision 2: API Endpoint Design

**Decision**: Implement 4 RESTful endpoints following existing project patterns

**Endpoints**:
1. `GET /schema` - Complete database schema
2. `GET /schema/tables/{table_name}` - Individual table schema
3. `GET /schema/relationships` - All foreign key relationships
4. `GET /schema/reference-data` - Reference table data with type filter

**Rationale**:
- RESTful resource-oriented design
- Follows existing project conventions (see `/accounts`, `/transactions`)
- Separates concerns (schema structure vs. data values)
- Provides both high-level overview and focused detail endpoints
- Query parameters for filtering (e.g., `?type=currencies`)

**Alternatives Considered**:
1. **Single endpoint with query parameters** - Rejected because:
   - Less RESTful (mixing different resource types)
   - Harder to document and discover
   - Complex parameter validation logic

2. **GraphQL schema introspection** - Rejected because:
   - Project uses REST, not GraphQL
   - Overkill for this use case
   - Would require new dependencies and patterns

### Decision 3: Response Format

**Decision**: Structured JSON with consistent field naming, following existing project patterns

**Schema**:
```json
{
  "tables": [
    {
      "name": "accounts",
      "type": "BASE TABLE",
      "columns": [
        {
          "column_name": "account_id",
          "data_type": "integer",
          "is_nullable": "NO",
          "column_default": "nextval('accounts_account_id_seq'::regclass)",
          "character_maximum_length": null,
          "numeric_precision": 32,
          "numeric_scale": 0
        }
      ],
      "constraints": [
        {
          "constraint_name": "accounts_pkey",
          "constraint_type": "PRIMARY KEY",
          "column_name": "account_id",
          "foreign_table_name": null,
          "foreign_column_name": null
        }
      ]
    }
  ],
  "relationships": [
    {
      "from_table": "transactions",
      "from_column": "account_id",
      "to_table": "accounts",
      "to_column": "account_id",
      "constraint_name": "transactions_account_id_fkey"
    }
  ]
}
```

**Rationale**:
- Matches PostgreSQL information_schema column names (familiar to SQL developers)
- Nested structure shows relationships clearly
- Includes all metadata needed for query construction
- Self-documenting field names

**Alternatives Considered**:
1. **Flat structure with relationship IDs** - Rejected because:
   - Less intuitive for consumers
   - Requires multiple lookups to understand relationships

2. **ERD/diagram format** - Rejected because:
   - Harder to parse programmatically
   - Use case is automated tooling, not human visualization

### Decision 4: Error Handling Strategy

**Decision**: Use existing project error response format with specific error codes

**Error Response Format**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Table 'nonexistent' not found in public schema",
    "details": {
      "table_name": "nonexistent",
      "schema": "public"
    }
  }
}
```

**Error Codes**:
- `NOT_FOUND` (404): Table doesn't exist
- `INVALID_PARAMETER` (422): Invalid reference data type
- `DATABASE_ERROR` (500): Connection or query failure

**Rationale**:
- Consistent with existing project error handling (see `accounts.py`, `transactions.py`)
- Provides actionable information for debugging
- Machine-readable error codes
- Details field for context-specific information

### Decision 5: Performance Optimization

**Decision**: No pagination for schema endpoints, caching considerations documented

**Rationale**:
- Database schemas are relatively small (15-20 tables typical)
- Complete schema response ~100-500KB (acceptable)
- Reference data queries filter by type (already scoped)
- Information_schema queries are fast (<100ms typical)

**Performance Safeguards**:
- Set response size limit (5MB max)
- Document that for very large databases (100+ tables), consider pagination
- Monitor query performance and response times

**Alternatives Considered**:
1. **Pagination for all endpoints** - Rejected because:
   - Unnecessary complexity for typical use case
   - Schema is needed as complete picture, not piecemeal
   - Reference data already filtered by type

2. **Response caching** - Deferred because:
   - Schema changes are infrequent (only during migrations)
   - Simplicity preferred for MVP
   - Can add later if performance becomes issue
   - Noted in implementation comments for future enhancement

## Best Practices Applied

### FastAPI Patterns
- Use `APIRouter` with prefix `/schema`
- Dependency injection for database session (`Depends(get_db)`)
- Pydantic models for response validation
- OpenAPI documentation with detailed descriptions
- Status codes: 200 (success), 404 (not found), 422 (validation), 500 (server error)

### Database Query Patterns
- Use SQLAlchemy `text()` for raw SQL with parameter binding
- Close sessions properly via dependency injection
- Handle `SQLAlchemyError` for database exceptions
- Log queries in development mode (already configured in `database.py`)

### Testing Patterns
- Integration tests with test database fixtures
- Mock database connection failures for error path testing
- Verify response schemas match Pydantic models
- Test edge cases (empty tables, no constraints, system tables filtered)

### Security Considerations
- Parameterized queries to prevent SQL injection
- Filter to `public` schema only (no system table exposure)
- No write operations (read-only endpoints)
- Rate limiting (existing FastAPI middleware applies)

## Implementation Sequence

Based on user story priorities (P1 → P2 → P3):

1. **Phase 1 (P1)**: Complete database schema endpoint
   - Implement `GET /schema` endpoint
   - Service layer for information_schema queries
   - Pydantic response models
   - Integration tests

2. **Phase 2 (P2)**: Individual table and relationships endpoints
   - Implement `GET /schema/tables/{table_name}`
   - Implement `GET /schema/relationships`
   - Error handling for non-existent tables
   - Relationship graph construction

3. **Phase 3 (P3)**: Reference data endpoint
   - Implement `GET /schema/reference-data?type={type}`
   - Filter by type (currencies, account_types, categories, all)
   - Filter for active records only

## Dependencies and Integration

**Existing Dependencies** (no new packages needed):
- `fastapi` - Web framework
- `sqlalchemy` - Database query execution
- `psycopg2-binary` - PostgreSQL driver
- `pydantic` - Response validation

**Integration Points**:
- Add router to `main.py` (existing pattern)
- Use existing `get_db()` dependency from `database.py`
- Follow existing service layer pattern (see `account_service.py`)
- Use existing error response format

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Large database schemas (100+ tables) | Response size/latency exceeds targets | Document limitations, consider pagination in future iteration |
| Schema changes during migration | Stale data returned | Information_schema is always current; no caching in MVP |
| SQL injection via table name parameter | Security vulnerability | Use parameterized queries, validate table names against information_schema |
| Database connection failures | 500 errors during schema queries | Proper exception handling, connection pool management (already configured) |
| Exposing sensitive metadata | Information disclosure | Filter to public schema only, document security considerations |

## Future Enhancements

*(Not in scope for MVP, documented for future consideration)*

1. **Response Caching**: Cache schema responses for 5-10 minutes (invalidate on migration)
2. **Pagination**: Add pagination for `/schema` endpoint if databases grow >50 tables
3. **Schema Versioning**: Track schema version with migrations for cache invalidation
4. **Extended Metadata**: Add table row counts, index information, table sizes
5. **Schema Comparison**: Endpoint to compare schemas across environments
6. **GraphQL Alternative**: GraphQL schema introspection for more flexible queries

## References

- PostgreSQL Information Schema Documentation: https://www.postgresql.org/docs/current/information-schema.html
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Existing Project Patterns: See `src/routers/accounts.py`, `src/services/account_service.py`
- Sample Reference: `/home/user1/ai-expense-app-bundle/ai-expense-tracker-agent/langgraph/react-pipeline/src/react_agent/tools/schema.py`
