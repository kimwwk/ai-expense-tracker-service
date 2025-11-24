# Quickstart: Database Schema Discovery API

**Feature**: 002-database-schema-api
**Date**: 2025-11-23
**Audience**: Developers implementing or using the schema discovery endpoints

## Overview

This guide provides step-by-step instructions for implementing and testing the Database Schema Discovery API. Follow this guide to quickly understand the feature and verify it works correctly.

## Prerequisites

- Python 3.11+ installed
- PostgreSQL database running with the expense tracker schema
- `uv` package manager installed
- Environment variables configured (`.env` file)
- Familiarity with FastAPI and SQLAlchemy

## Implementation Checklist

### Phase 1: Core Schema Endpoint (P1)

**Goal**: Implement `GET /schema` to retrieve complete database schema

- [ ] Create `src/schemas/schema.py` with Pydantic models
  - [ ] `ColumnDefinition` model
  - [ ] `ConstraintDefinition` model
  - [ ] `TableSchema` model
  - [ ] `DatabaseSchema` model

- [ ] Create `src/services/schema_service.py` with service functions
  - [ ] `get_complete_schema(db: Session) -> DatabaseSchema`
  - [ ] Helper: Query all tables from information_schema
  - [ ] Helper: Query columns for each table
  - [ ] Helper: Query constraints for each table
  - [ ] Helper: Extract foreign key relationships

- [ ] Create `src/routers/schema.py` with router
  - [ ] Define router with prefix `/schema` and tag `["schema"]`
  - [ ] Implement `GET /schema` endpoint
  - [ ] Add error handling for database errors
  - [ ] Add comprehensive docstrings

- [ ] Register router in `src/main.py`
  - [ ] Import schema router
  - [ ] Add `app.include_router(schema.router)`

- [ ] Write integration tests in `tests/integration/test_schema_api.py`
  - [ ] Test successful schema retrieval
  - [ ] Verify all tables returned
  - [ ] Verify columns match database
  - [ ] Verify constraints included
  - [ ] Test error handling (database connection failure)

### Phase 2: Table and Relationships Endpoints (P2)

**Goal**: Implement focused endpoints for individual tables and relationships

- [ ] Update `src/schemas/schema.py`
  - [ ] `TableRelationship` model

- [ ] Update `src/services/schema_service.py`
  - [ ] `get_table_schema(db: Session, table_name: str) -> Optional[TableSchema]`
  - [ ] `get_table_relationships(db: Session) -> List[TableRelationship]`

- [ ] Update `src/routers/schema.py`
  - [ ] Implement `GET /schema/tables/{table_name}` endpoint
  - [ ] Implement `GET /schema/relationships` endpoint
  - [ ] Add 404 error handling for non-existent tables
  - [ ] Add validation for table names

- [ ] Write integration tests
  - [ ] Test table schema retrieval for existing table
  - [ ] Test 404 for non-existent table
  - [ ] Test relationships endpoint
  - [ ] Verify foreign key relationships correct

### Phase 3: Reference Data Endpoint (P3)

**Goal**: Implement reference data retrieval with type filtering

- [ ] Update `src/schemas/schema.py`
  - [ ] `ReferenceDataResponse` model

- [ ] Update `src/services/schema_service.py`
  - [ ] `get_reference_data(db: Session, data_type: str) -> ReferenceDataResponse`
  - [ ] Query currencies table
  - [ ] Query account_types table
  - [ ] Query categories table
  - [ ] Handle type="all" case

- [ ] Update `src/routers/schema.py`
  - [ ] Implement `GET /schema/reference-data?type={type}` endpoint
  - [ ] Add query parameter validation
  - [ ] Add 422 error for invalid type
  - [ ] Filter active records only

- [ ] Write integration tests
  - [ ] Test each reference data type individually
  - [ ] Test type="all" returns all types
  - [ ] Test 422 for invalid type
  - [ ] Verify only active records returned

### Phase 4: Documentation and Polish

- [ ] Update OpenAPI documentation
  - [ ] Verify all endpoints documented
  - [ ] Add examples for each endpoint
  - [ ] Test in Swagger UI (`/docs`)

- [ ] Add logging
  - [ ] Log schema retrieval requests
  - [ ] Log errors with context

- [ ] Performance testing
  - [ ] Measure response times for each endpoint
  - [ ] Verify meets performance targets (<200ms, <2s)

## Quick Start Commands

### 1. Setup Environment

```bash
# Install dependencies
cd /home/user1/ai-expense-app-bundle/ai-expense-tracker-service
uv sync --dev

# Verify database connection
uv run python -c "from src.database import engine; engine.connect(); print('Database connected')"
```

### 2. Run Development Server

```bash
# Start the API server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. Test Endpoints Manually

```bash
# Test complete schema endpoint
curl http://localhost:8000/schema | jq .

# Test specific table schema
curl http://localhost:8000/schema/tables/accounts | jq .

# Test relationships endpoint
curl http://localhost:8000/schema/relationships | jq .

# Test reference data endpoint
curl 'http://localhost:8000/schema/reference-data?type=currencies' | jq .

# Test error handling (non-existent table)
curl http://localhost:8000/schema/tables/nonexistent | jq .
```

### 4. Run Tests

```bash
# Run all integration tests
uv run pytest tests/integration/test_schema_api.py -v

# Run with coverage
uv run pytest tests/integration/test_schema_api.py --cov=src/services/schema_service --cov=src/routers/schema --cov-report=term-missing

# Run specific test
uv run pytest tests/integration/test_schema_api.py::test_get_complete_schema -v
```

## Example Usage

### Python Client Example

```python
import httpx

# Fetch complete schema
response = httpx.get("http://localhost:8000/schema")
schema = response.json()

print(f"Found {len(schema['tables'])} tables")
for table in schema['tables']:
    print(f"  - {table['name']} ({len(table['columns'])} columns)")

# Fetch specific table schema
response = httpx.get("http://localhost:8000/schema/tables/accounts")
table_schema = response.json()

print(f"\nTable: {table_schema['name']}")
print("Columns:")
for col in table_schema['columns']:
    nullable = "NULL" if col['is_nullable'] == "YES" else "NOT NULL"
    print(f"  - {col['column_name']}: {col['data_type']} {nullable}")

# Fetch reference data
response = httpx.get("http://localhost:8000/schema/reference-data?type=currencies")
ref_data = response.json()

print("\nCurrencies:")
for currency in ref_data['data']:
    print(f"  - {currency['currency_code']}: {currency['currency_name']} ({currency['currency_symbol']})")
```

### JavaScript/TypeScript Example

```typescript
// Fetch complete schema
const schemaResponse = await fetch('http://localhost:8000/schema');
const schema = await schemaResponse.json();

console.log(`Found ${schema.tables.length} tables`);

// Fetch table relationships
const relationshipsResponse = await fetch('http://localhost:8000/schema/relationships');
const relationships = await relationshipsResponse.json();

// Build relationship map for UI
const relationshipMap = relationships.reduce((acc, rel) => {
  if (!acc[rel.from_table]) acc[rel.from_table] = [];
  acc[rel.from_table].push({
    column: rel.from_column,
    references: `${rel.to_table}.${rel.to_column}`
  });
  return acc;
}, {});

console.log('Relationships:', relationshipMap);
```

### cURL Examples

```bash
# Get complete schema (pretty-printed)
curl -s http://localhost:8000/schema | jq '{table_count: (.tables | length), tables: [.tables[].name]}'

# Get specific table with error handling
curl -s http://localhost:8000/schema/tables/accounts || echo "Table not found"

# Get all reference data types
curl -s 'http://localhost:8000/schema/reference-data?type=all' | jq 'keys'

# Check if table exists
TABLE="accounts"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/schema/tables/$TABLE)
if [ "$STATUS" -eq 200 ]; then
  echo "Table $TABLE exists"
else
  echo "Table $TABLE not found"
fi
```

## Verification Steps

After implementing each phase, verify:

### Phase 1 Verification

1. **Schema endpoint returns data**:
   ```bash
   curl http://localhost:8000/schema | jq '.tables | length'
   # Should return number > 0
   ```

2. **All expected tables present**:
   ```bash
   curl http://localhost:8000/schema | jq '.tables[].name' | grep accounts
   # Should find "accounts" table
   ```

3. **Columns include all metadata**:
   ```bash
   curl http://localhost:8000/schema | jq '.tables[0].columns[0]'
   # Should show column_name, data_type, is_nullable, etc.
   ```

4. **Relationships extracted**:
   ```bash
   curl http://localhost:8000/schema | jq '.relationships | length'
   # Should return number > 0
   ```

### Phase 2 Verification

1. **Single table retrieval works**:
   ```bash
   curl http://localhost:8000/schema/tables/accounts | jq '.name'
   # Should return "accounts"
   ```

2. **404 for non-existent table**:
   ```bash
   curl -w "\n%{http_code}\n" http://localhost:8000/schema/tables/nonexistent
   # Should return 404
   ```

3. **Relationships endpoint works**:
   ```bash
   curl http://localhost:8000/schema/relationships | jq '.[0]'
   # Should show from_table, to_table, etc.
   ```

### Phase 3 Verification

1. **Currency reference data**:
   ```bash
   curl 'http://localhost:8000/schema/reference-data?type=currencies' | jq '.data | length'
   # Should return number of active currencies
   ```

2. **All reference data types**:
   ```bash
   curl 'http://localhost:8000/schema/reference-data?type=all' | jq '.data | keys'
   # Should return ["account_types", "categories", "currencies"]
   ```

3. **Invalid type returns 422**:
   ```bash
   curl -w "\n%{http_code}\n" 'http://localhost:8000/schema/reference-data?type=invalid'
   # Should return 422
   ```

## Troubleshooting

### Issue: Empty tables array returned

**Cause**: Database connection issue or no tables in public schema

**Solution**:
```bash
# Verify database connection
uv run python -c "from src.database import engine; print(engine.url)"

# Check for tables in public schema
psql -d your_database -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
```

### Issue: 500 error on schema endpoint

**Cause**: SQL query error or information_schema access denied

**Solution**:
- Check server logs for SQL error details
- Verify database user has SELECT permission on information_schema
- Test query directly in psql:
  ```sql
  SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
  ```

### Issue: Foreign key relationships missing

**Cause**: Constraints query not returning expected results

**Solution**:
- Verify foreign keys exist in database:
  ```sql
  SELECT * FROM information_schema.table_constraints
  WHERE table_schema = 'public' AND constraint_type = 'FOREIGN KEY';
  ```
- Check service layer query for foreign key extraction

### Issue: Reference data returns inactive records

**Cause**: is_active filter not applied correctly

**Solution**:
- Review SQL query in service layer
- Ensure `WHERE is_active = TRUE` clause present
- Note: Not all reference tables may have is_active column

## Performance Benchmarks

Expected response times (measured on typical development machine):

| Endpoint | Expected Latency | Notes |
|----------|------------------|-------|
| `GET /schema` | <2000ms | For ~20 tables |
| `GET /schema/tables/{name}` | <200ms | Single table query |
| `GET /schema/relationships` | <200ms | Foreign keys only |
| `GET /schema/reference-data?type=currencies` | <100ms | Small table (<100 rows) |
| `GET /schema/reference-data?type=all` | <500ms | All reference tables |

If response times significantly exceed these targets:
- Check database connection latency
- Review SQL query execution plans
- Consider adding indexes on information_schema queries (unlikely needed)
- Monitor database load

## Next Steps

After completing implementation:

1. **Run `/speckit.tasks`** to generate detailed implementation tasks
2. **Create feature branch tests** to verify end-to-end functionality
3. **Update main API documentation** with new endpoints
4. **Create user-facing guide** for consuming the schema API (if needed)
5. **Performance test** with production-like data volume

## Related Documentation

- [Feature Specification](./spec.md) - Business requirements and user stories
- [Implementation Plan](./plan.md) - Technical approach and architecture
- [Data Model](./data-model.md) - Response schemas and validation rules
- [API Contracts](./contracts/openapi.yaml) - OpenAPI specification
- [Research Notes](./research.md) - Technical decisions and alternatives
