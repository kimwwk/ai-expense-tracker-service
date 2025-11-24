"""
Pydantic models for database schema discovery API responses.
These models represent metadata from PostgreSQL's information_schema views.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, ConfigDict


class ColumnDefinition(BaseModel):
    """Column metadata from information_schema.columns"""
    column_name: str
    data_type: str
    is_nullable: str  # "YES" or "NO" from information_schema
    column_default: Optional[str] = None
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class ConstraintDefinition(BaseModel):
    """Constraint metadata from information_schema.table_constraints"""
    constraint_name: str
    constraint_type: str  # "PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK"
    column_name: Optional[str] = None
    foreign_table_name: Optional[str] = None
    foreign_column_name: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "constraint_name": "transactions_account_id_fkey",
                "constraint_type": "FOREIGN KEY",
                "column_name": "account_id",
                "foreign_table_name": "accounts",
                "foreign_column_name": "account_id"
            }
        }
    )


class TableSchema(BaseModel):
    """Complete schema information for a single table"""
    name: str
    type: str  # "BASE TABLE" or "VIEW"
    columns: List[ColumnDefinition]
    constraints: List[ConstraintDefinition]

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class TableRelationship(BaseModel):
    """Foreign key relationship between tables"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    constraint_name: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "from_table": "transactions",
                "from_column": "account_id",
                "to_table": "accounts",
                "to_column": "account_id",
                "constraint_name": "transactions_account_id_fkey"
            }
        }
    )


class DatabaseSchema(BaseModel):
    """Complete database schema information"""
    tables: List[TableSchema]
    relationships: List[TableRelationship]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tables": [
                    {
                        "name": "accounts",
                        "type": "BASE TABLE",
                        "columns": [],
                        "constraints": []
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
    )


class ReferenceDataResponse(BaseModel):
    """Response for reference data queries"""
    data_type: str  # "currencies", "account_types", "categories", "all"
    data: Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
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
                {
                    "data_type": "all",
                    "data": {
                        "currencies": [],
                        "account_types": [],
                        "categories": []
                    }
                }
            ]
        }
    )
