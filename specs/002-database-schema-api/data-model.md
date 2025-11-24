# Data Model: Database Schema Discovery API

**Feature**: 002-database-schema-api
**Date**: 2025-11-23
**Purpose**: Define the response data structures for schema discovery endpoints

## Overview

This document defines the Pydantic models used for API responses in the schema discovery feature. These models represent database metadata retrieved from PostgreSQL's `information_schema` views, not application domain entities.

**Note**: This feature does NOT create or modify database tables. It queries existing metadata about the database structure.

## Response Models

### 1. ColumnDefinition

Represents detailed information about a table column.

```python
class ColumnDefinition(BaseModel):
    """Column metadata from information_schema.columns"""
    column_name: str
    data_type: str
    is_nullable: str  # "YES" or "NO" from information_schema
    column_default: Optional[str] = None
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "column_name": "account_id",
                "data_type": "integer",
                "is_nullable": "NO",
                "column_default": "nextval('accounts_account_id_seq'::regclass)",
                "character_maximum_length": None,
                "numeric_precision": 32,
                "numeric_scale": 0
            }
        }
```

**Field Descriptions**:
- `column_name`: Name of the column
- `data_type`: PostgreSQL data type (integer, varchar, timestamp, etc.)
- `is_nullable`: Whether column accepts NULL values ("YES"/"NO")
- `column_default`: Default value expression (if any)
- `character_maximum_length`: Max length for character types (varchar, char)
- `numeric_precision`: Total digits for numeric types
- `numeric_scale`: Decimal places for numeric types

**Validation Rules**:
- All fields match information_schema.columns structure
- Nullable fields use `Optional[T]`
- No custom business logic validation needed

### 2. ConstraintDefinition

Represents a table constraint (primary key, foreign key, unique, check).

```python
class ConstraintDefinition(BaseModel):
    """Constraint metadata from information_schema.table_constraints"""
    constraint_name: str
    constraint_type: str  # "PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK"
    column_name: Optional[str] = None
    foreign_table_name: Optional[str] = None
    foreign_column_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "constraint_name": "transactions_account_id_fkey",
                "constraint_type": "FOREIGN KEY",
                "column_name": "account_id",
                "foreign_table_name": "accounts",
                "foreign_column_name": "account_id"
            }
        }
```

**Field Descriptions**:
- `constraint_name`: Name of the constraint in the database
- `constraint_type`: Type of constraint (from information_schema)
- `column_name`: Column affected by constraint (NULL for table-level constraints)
- `foreign_table_name`: Referenced table (for FOREIGN KEY only)
- `foreign_column_name`: Referenced column (for FOREIGN KEY only)

**Validation Rules**:
- `foreign_table_name` and `foreign_column_name` only populated for FOREIGN KEY constraints
- `constraint_type` is one of the standard PostgreSQL types

### 3. TableSchema

Represents the complete structure of a single table.

```python
class TableSchema(BaseModel):
    """Complete schema information for a single table"""
    name: str
    type: str  # "BASE TABLE" or "VIEW"
    columns: List[ColumnDefinition]
    constraints: List[ConstraintDefinition]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "accounts",
                "type": "BASE TABLE",
                "columns": [
                    {
                        "column_name": "account_id",
                        "data_type": "integer",
                        "is_nullable": "NO",
                        "column_default": "nextval('accounts_account_id_seq'::regclass)",
                        "character_maximum_length": None,
                        "numeric_precision": 32,
                        "numeric_scale": 0
                    }
                ],
                "constraints": [
                    {
                        "constraint_name": "accounts_pkey",
                        "constraint_type": "PRIMARY KEY",
                        "column_name": "account_id",
                        "foreign_table_name": None,
                        "foreign_column_name": None
                    }
                ]
            }
        }
```

**Field Descriptions**:
- `name`: Table name
- `type`: Table type from information_schema (usually "BASE TABLE")
- `columns`: List of all columns in ordinal position order
- `constraints`: List of all constraints defined on the table

**Validation Rules**:
- `columns` list ordered by `ordinal_position` from information_schema
- Empty `constraints` list if no constraints defined (not an error)

### 4. TableRelationship

Represents a foreign key relationship between two tables.

```python
class TableRelationship(BaseModel):
    """Foreign key relationship between tables"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    constraint_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "from_table": "transactions",
                "from_column": "account_id",
                "to_table": "accounts",
                "to_column": "account_id",
                "constraint_name": "transactions_account_id_fkey"
            }
        }
```

**Field Descriptions**:
- `from_table`: Source table containing foreign key
- `from_column`: Column in source table
- `to_table`: Target table being referenced
- `to_column`: Column in target table
- `constraint_name`: Name of the foreign key constraint

**Validation Rules**:
- All fields are required (foreign keys always have these properties)
- Represents directed relationship (from → to)

### 5. DatabaseSchema

Represents the complete database schema (all tables and relationships).

```python
class DatabaseSchema(BaseModel):
    """Complete database schema information"""
    tables: List[TableSchema]
    relationships: List[TableRelationship]

    class Config:
        json_schema_extra = {
            "example": {
                "tables": [
                    {
                        "name": "accounts",
                        "type": "BASE TABLE",
                        "columns": [...],
                        "constraints": [...]
                    },
                    {
                        "name": "transactions",
                        "type": "BASE TABLE",
                        "columns": [...],
                        "constraints": [...]
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
        }
```

**Field Descriptions**:
- `tables`: List of all tables in the public schema
- `relationships`: List of all foreign key relationships

**Validation Rules**:
- Tables sorted alphabetically by name
- Relationships extracted from constraint definitions across all tables

### 6. ReferenceDataItem

Represents a single record from a reference/lookup table.

```python
class ReferenceDataItem(BaseModel):
    """Generic reference data record (structure varies by type)"""
    # Currency example
    currency_code: Optional[str] = None
    currency_name: Optional[str] = None
    currency_symbol: Optional[str] = None
    decimal_places: Optional[int] = None
    is_active: Optional[bool] = None

    # Account Type example
    account_type_id: Optional[int] = None
    type_name: Optional[str] = None
    description: Optional[str] = None
    is_asset: Optional[bool] = None

    # Category example
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_group: Optional[str] = None
    category_type: Optional[str] = None
    color_code: Optional[str] = None
    icon_name: Optional[str] = None

    class Config:
        extra = "allow"  # Allow additional fields from database
        json_schema_extra = {
            "example": {
                "currency_code": "USD",
                "currency_name": "US Dollar",
                "currency_symbol": "$",
                "decimal_places": 2,
                "is_active": True
            }
        }
```

**Field Descriptions**:
- Fields vary based on reference table queried
- All fields optional to accommodate different table structures
- `extra = "allow"` permits additional fields not explicitly defined

**Validation Rules**:
- Use `Dict[str, Any]` for maximum flexibility
- Service layer constructs from database rows dynamically
- No strict schema validation (reflects actual table structure)

**Alternative Implementation** (simpler):
```python
ReferenceDataItem = Dict[str, Any]  # Type alias for flexibility
```

### 7. ReferenceDataResponse

Wrapper for reference data query results.

```python
class ReferenceDataResponse(BaseModel):
    """Response for reference data queries"""
    data_type: str  # "currencies", "account_types", "categories", "all"
    data: Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]

    class Config:
        json_schema_extra = {
            "example_single": {
                "data_type": "currencies",
                "data": [
                    {
                        "currency_code": "USD",
                        "currency_name": "US Dollar",
                        "currency_symbol": "$",
                        "decimal_places": 2,
                        "is_active": True
                    }
                ]
            },
            "example_all": {
                "data_type": "all",
                "data": {
                    "currencies": [...],
                    "account_types": [...],
                    "categories": [...]
                }
            }
        }
```

**Field Descriptions**:
- `data_type`: Type of reference data requested
- `data`: List of records (single type) or dict of lists (type "all")

**Validation Rules**:
- `data` is `List[Dict]` when single type requested
- `data` is `Dict[str, List[Dict]]` when type="all"
- Keys in dict match requested types

## Entity Relationships

```text
DatabaseSchema
├── tables: List[TableSchema]
│   ├── columns: List[ColumnDefinition]
│   └── constraints: List[ConstraintDefinition]
└── relationships: List[TableRelationship]
```

**Cardinality**:
- 1 DatabaseSchema contains N TableSchema
- 1 TableSchema contains N ColumnDefinition
- 1 TableSchema contains N ConstraintDefinition
- 1 DatabaseSchema contains N TableRelationship
- Relationships are derived from foreign key constraints across tables

## State Transitions

**Not Applicable**: This feature is read-only. No state transitions or lifecycle management needed.

The data models represent snapshots of database metadata at query time. Schema changes occur via database migrations, not through these endpoints.

## Validation Rules Summary

### Required Fields
- All models have required fields based on information_schema guarantees
- `Optional[T]` used for nullable information_schema columns

### Data Type Constraints
- `is_nullable`: String literal "YES" or "NO" (from information_schema)
- `constraint_type`: String from fixed set ("PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK")
- `data_type`: PostgreSQL type names (varchar, integer, timestamp, etc.)

### Business Rules
- Filter to `table_schema = 'public'` (no system tables)
- Reference data filters for `is_active = TRUE` where applicable
- Tables ordered alphabetically
- Columns ordered by ordinal_position
- Relationships ordered by source table, then source column

### Error Conditions
- Table not found in public schema → 404 error
- Invalid reference data type → 422 error with valid options
- Database connection failure → 500 error
- Query execution error → 500 error with details

## Model Usage by Endpoint

| Endpoint | Request | Response Model |
|----------|---------|----------------|
| `GET /schema` | None | `DatabaseSchema` |
| `GET /schema/tables/{table_name}` | Path param: `table_name` | `TableSchema` |
| `GET /schema/relationships` | None | `List[TableRelationship]` |
| `GET /schema/reference-data` | Query param: `type` | `ReferenceDataResponse` |

## Implementation Notes

### Pydantic Configuration
- Use `orm_mode = False` (not mapping from ORM models)
- Use `json_schema_extra` for OpenAPI examples
- Set `extra = "forbid"` for strict validation (except ReferenceDataItem)

### Performance Considerations
- No lazy loading (all data fetched in single query per endpoint)
- Response models serialize efficiently (flat structures)
- Large schemas (~50 tables) result in ~100-500KB responses

### Testing Strategy
- Unit tests: Validate model serialization from mock data
- Integration tests: Verify models match actual information_schema queries
- Contract tests: Validate OpenAPI schema matches Pydantic models
