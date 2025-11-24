# Quickstart Guide: Table Names List Endpoint

**Feature**: 003-list-tables
**Estimated Time**: 30-60 minutes
**Difficulty**: Easy (extends existing patterns)

## Prerequisites

- Feature 002 (Database Schema Discovery API) is complete and working
- Python 3.11+ with FastAPI, SQLAlchemy, Pydantic installed
- PostgreSQL database with expense tracker schema
- Development server can start successfully

## Implementation Checklist

### Phase 1: Service Layer (15 min)

- [ ] Open `src/services/schema_service.py`
- [ ] Add `get_table_names(db: Session) -> List[str]` function
- [ ] Query `information_schema.tables` WHERE `table_schema = 'public'` AND `table_type = 'BASE TABLE'`
- [ ] Sort results by `table_name` in SQL query
- [ ] Extract table names using list comprehension: `[row.table_name for row in result]`
- [ ] Add logging: `logger.info(f"Retrieved {len(table_names)} table names")`
- [ ] Return list of strings

**Expected Output**: Function that returns `["account_types", "accounts", "categories", ...]`

### Phase 2: Router Endpoint (10 min)

- [ ] Open `src/routers/schema.py`
- [ ] Add new endpoint: `@router.get("/tables", response_model=List[str])`
- [ ] Import `List` from typing if not already imported
- [ ] Create endpoint function: `get_table_names_endpoint(db: Session = Depends(get_db))`
- [ ] Call service function: `table_names = schema_service.get_table_names(db)`
- [ ] Add error handling (SQLAlchemyError → HTTP 500)
- [ ] Add logging for requests and errors
- [ ] Return table names list

**Expected Output**: Endpoint accessible at `GET /schema/tables`

### Phase 3: Unit Tests (15 min)

- [ ] Create `tests/unit/test_schema_service.py` (if doesn't exist)
- [ ] Write test: `test_get_table_names_returns_sorted_list()`
  - Call `schema_service.get_table_names(db_session)`
  - Assert result is a list
  - Assert all items are strings
  - Assert list is sorted alphabetically
  - Assert known tables are present (e.g., "accounts", "transactions")
- [ ] Write test: `test_get_table_names_excludes_views()`
  - Create a test view in database
  - Call function
  - Assert view name not in result
  - Drop test view
- [ ] Run tests: `pytest tests/unit/test_schema_service.py -v`

**Expected Output**: All unit tests pass

### Phase 4: Integration Tests (15 min)

- [ ] Open `tests/integration/test_schema_api.py`
- [ ] Add test: `test_get_table_names_success()`
  - Use TestClient to GET `/schema/tables`
  - Assert status code 200
  - Assert response is JSON array
  - Assert array contains expected table names
  - Assert array is sorted alphabetically
- [ ] Add test: `test_get_table_names_performance()`
  - Measure response time
  - Assert < 100ms
- [ ] Run tests: `pytest tests/integration/test_schema_api.py -v`

**Expected Output**: All integration tests pass

### Phase 5: Manual Verification (10 min)

- [ ] Start development server: `uvicorn src.main:app --reload`
- [ ] Open browser: `http://localhost:8000/docs`
- [ ] Verify `/schema/tables` endpoint appears in OpenAPI docs
- [ ] Click "Try it out" → "Execute"
- [ ] Verify response is an array of table names
- [ ] Verify response matches expected tables
- [ ] Test with curl: `curl http://localhost:8000/schema/tables`
- [ ] Verify JSON response is valid and sorted

**Expected Output**: Endpoint works correctly via Swagger UI and curl

## Code Templates

### Service Function Template

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

### Router Endpoint Template

```python
@router.get(
    "/tables",
    response_model=List[str],
    summary="Get all table names"
)
def get_table_names_endpoint(db: Session = Depends(get_db)):
    """Get list of all table names from the public schema."""
    try:
        logger.info("Retrieving table names")
        table_names = schema_service.get_table_names(db)
        logger.info(f"Successfully retrieved {len(table_names)} table names")
        return table_names
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving table names: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DATABASE_ERROR", "message": "Failed to retrieve table names"}}
        )
    except Exception as e:
        logger.error(f"Unexpected error while retrieving table names: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}
        )
```

### Unit Test Template

```python
def test_get_table_names_returns_sorted_list(db_session):
    """Test that get_table_names returns a sorted list of table names."""
    # Arrange
    # (use existing database with known tables)

    # Act
    table_names = schema_service.get_table_names(db_session)

    # Assert
    assert isinstance(table_names, list)
    assert len(table_names) > 0
    assert all(isinstance(name, str) for name in table_names)
    assert table_names == sorted(table_names), "Table names should be sorted alphabetically"

    # Verify expected tables are present
    expected_tables = ["accounts", "transactions", "categories"]
    for table in expected_tables:
        assert table in table_names, f"Expected table '{table}' not found"
```

### Integration Test Template

```python
def test_get_table_names_success(test_client):
    """Test GET /schema/tables returns table names successfully."""
    # Act
    response = test_client.get("/schema/tables")

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    table_names = response.json()
    assert isinstance(table_names, list)
    assert len(table_names) > 0
    assert all(isinstance(name, str) for name in table_names)
    assert table_names == sorted(table_names), "Table names should be sorted"

    # Verify expected tables
    expected_tables = ["accounts", "transactions", "categories"]
    for table in expected_tables:
        assert table in table_names
```

## Testing Examples

### Test with curl

```bash
# Basic request
curl http://localhost:8000/schema/tables

# With headers
curl -i http://localhost:8000/schema/tables

# Measure performance
time curl http://localhost:8000/schema/tables

# Pretty print JSON
curl http://localhost:8000/schema/tables | jq '.'
```

**Expected Response**:
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

### Test with Python

```python
import requests

# Get table names
response = requests.get("http://localhost:8000/schema/tables")
table_names = response.json()

print(f"Found {len(table_names)} tables:")
for name in table_names:
    print(f"  - {name}")
```

## Troubleshooting

### Issue: Empty array returned

**Cause**: No tables in public schema (unlikely in production)

**Solution**:
- Verify database connection
- Check that migrations have been run
- Query directly: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'`

### Issue: System tables appearing in results

**Cause**: Query not filtering by table_type

**Solution**:
- Ensure query includes `AND table_type = 'BASE TABLE'`
- Verify no views are being returned

### Issue: Response time > 100ms

**Cause**: Database connection latency or slow query

**Solution**:
- Check database connection pool settings
- Verify query plan: `EXPLAIN ANALYZE SELECT ...`
- Consider connection pooling optimization

### Issue: Endpoint not appearing in /docs

**Cause**: Router not registered or OpenAPI schema issues

**Solution**:
- Verify router is imported in `src/main.py`
- Check that `@router.get()` decorator is correct
- Restart development server
- Clear browser cache

## Performance Benchmarks

**Target**: <100ms response time

**Expected Breakdown**:
- Database query: <10ms
- JSON serialization: <1ms
- Network overhead: <90ms

**Actual Measurement**:
```bash
# Run multiple times to get average
for i in {1..10}; do
  time curl -s http://localhost:8000/schema/tables > /dev/null
done
```

## Next Steps

After completing this implementation:

1. **Run full test suite**: `pytest tests/ -v`
2. **Check OpenAPI docs**: Verify endpoint documentation is clear
3. **Performance test**: Verify <100ms target is met
4. **Code review**: Ensure code follows existing patterns
5. **Commit changes**: Create feature branch commit
6. **Consider**: Do any clients need this endpoint immediately?

## Related Documentation

- Feature 002 Spec: `specs/002-database-schema-api/spec.md`
- Feature 002 Implementation: `src/routers/schema.py`, `src/services/schema_service.py`
- PostgreSQL information_schema: https://www.postgresql.org/docs/current/information-schema.html
- FastAPI List Responses: https://fastapi.tiangolo.com/tutorial/response-model/
