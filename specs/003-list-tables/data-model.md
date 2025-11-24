# Data Model: Table Names List Endpoint

**Feature**: 003-list-tables
**Date**: 2025-11-24

## Overview

This feature has minimal data modeling requirements since it returns a simple list of strings (table names). No new Pydantic models are needed.

## Response Model

### TableNamesList

**Type**: `List[str]`

**Description**: A simple array of table names from the public schema, sorted alphabetically.

**Usage**: Direct FastAPI response_model annotation:
```python
@router.get("/tables", response_model=List[str])
def get_table_names_endpoint(db: Session = Depends(get_db)):
    ...
```

**Validation Rules**:
- FastAPI automatically validates that response is a list
- Each element must be a string
- No additional validation needed (table names are already validated by PostgreSQL)

**Example Response**:
```json
[
  "account_types",
  "accounts",
  "categories",
  "currencies",
  "payees",
  "transactions",
  "transaction_splits",
  "users"
]
```

## Database Schema (Read-Only)

This feature queries existing database metadata, no schema changes required.

### Source: information_schema.tables

**Description**: PostgreSQL system view containing table metadata

**Columns Used**:
- `table_schema` (string): Schema name (filtered to 'public')
- `table_name` (string): Name of the table
- `table_type` (string): Type of table (filtered to 'BASE TABLE')

**Query**:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

## Service Layer Data Flow

```
Client Request
    ↓
GET /schema/tables
    ↓
schema_router.get_table_names_endpoint()
    ↓
schema_service.get_table_names(db)
    ↓
Query: information_schema.tables
    ↓
PostgreSQL
    ↓
Result: List[Row(table_name)]
    ↓
Transform: [row.table_name for row in result]
    ↓
Return: List[str]
    ↓
FastAPI JSON Serialization
    ↓
HTTP Response: ["table1", "table2", ...]
```

## Type Signatures

### Service Function

```python
def get_table_names(db: Session) -> List[str]:
    """
    Retrieve all table names from the public schema.

    Args:
        db: SQLAlchemy database session

    Returns:
        List of table names sorted alphabetically

    Raises:
        SQLAlchemyError: If database query fails
    """
```

### Router Endpoint

```python
@router.get("/tables", response_model=List[str])
def get_table_names_endpoint(
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Get list of all table names from the public schema.

    Returns:
        List of table names sorted alphabetically

    Raises:
        HTTPException: 500 if database query fails
    """
```

## Error Responses

### Database Error

**HTTP Status**: 500 Internal Server Error

**Response Model**: Follows existing error pattern from schema router

```json
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Failed to retrieve table names"
  }
}
```

### Empty Schema (Valid Response)

**HTTP Status**: 200 OK

**Response**:
```json
[]
```

**Note**: Empty array is a valid response when no tables exist in the public schema.

## Comparison with Existing Endpoints

| Endpoint | Response Type | Complexity | Use Case |
|----------|--------------|------------|----------|
| `GET /schema` | DatabaseSchema (complex) | High | Full schema discovery |
| `GET /schema/tables/{name}` | TableSchema (medium) | Medium | Single table details |
| `GET /schema/tables` (NEW) | List[str] (simple) | Low | Quick table list |
| `GET /schema/relationships` | List[TableRelationship] | Medium | Foreign key graph |

**Rationale**: This endpoint fills the gap for lightweight table discovery without the overhead of full schema metadata.

## OpenAPI Schema Definition

**Response Schema**:
```yaml
type: array
items:
  type: string
minItems: 0
example:
  - "account_types"
  - "accounts"
  - "categories"
  - "currencies"
  - "payees"
  - "transactions"
  - "transaction_splits"
  - "users"
```

**No Request Body**: GET endpoint with no parameters

**No Query Parameters**: Returns all tables (no filtering)

## Notes

1. **No Pydantic Models Needed**: `List[str]` is sufficient for this simple response
2. **Immutable Response**: Table names don't change during request processing
3. **Deterministic**: Same query always returns same results (until schema migration)
4. **Cacheable**: Response could be cached (though not required for MVP)
5. **Idempotent**: Multiple requests return same result (safe to retry)
