"""
Database schema discovery service layer.
Queries PostgreSQL's information_schema views to retrieve schema metadata.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.schemas.schema import (
    ColumnDefinition,
    ConstraintDefinition,
    TableSchema,
    TableRelationship,
    DatabaseSchema,
    ReferenceDataResponse
)

logger = logging.getLogger(__name__)


def get_all_tables(db: Session) -> List[Dict[str, Any]]:
    """
    Retrieve all tables from the public schema.

    Args:
        db: Database session

    Returns:
        List of dictionaries containing table_name and table_type
    """
    query = text("""
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)

    result = db.execute(query)
    tables = [{"table_name": row.table_name, "table_type": row.table_type} for row in result]
    logger.info(f"Retrieved {len(tables)} tables from public schema")
    return tables


def get_table_columns(db: Session, table_name: str) -> List[ColumnDefinition]:
    """
    Retrieve all columns for a specific table.

    Args:
        db: Database session
        table_name: Name of the table

    Returns:
        List of ColumnDefinition objects
    """
    query = text("""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = :table_name
        ORDER BY ordinal_position
    """)

    result = db.execute(query, {"table_name": table_name})
    columns = []
    for row in result:
        columns.append(ColumnDefinition(
            column_name=row.column_name,
            data_type=row.data_type,
            is_nullable=row.is_nullable,
            column_default=row.column_default,
            character_maximum_length=row.character_maximum_length,
            numeric_precision=row.numeric_precision,
            numeric_scale=row.numeric_scale
        ))

    logger.debug(f"Retrieved {len(columns)} columns for table {table_name}")
    return columns


def get_table_constraints(db: Session, table_name: str) -> List[ConstraintDefinition]:
    """
    Retrieve all constraints for a specific table.

    Args:
        db: Database session
        table_name: Name of the table

    Returns:
        List of ConstraintDefinition objects
    """
    query = text("""
        SELECT
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        LEFT JOIN information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
            AND tc.table_schema = ccu.table_schema
        WHERE tc.table_schema = 'public' AND tc.table_name = :table_name
        ORDER BY tc.constraint_name
    """)

    result = db.execute(query, {"table_name": table_name})
    constraints = []
    for row in result:
        constraints.append(ConstraintDefinition(
            constraint_name=row.constraint_name,
            constraint_type=row.constraint_type,
            column_name=row.column_name,
            foreign_table_name=row.foreign_table_name,
            foreign_column_name=row.foreign_column_name
        ))

    logger.debug(f"Retrieved {len(constraints)} constraints for table {table_name}")
    return constraints


def extract_relationships(db: Session) -> List[TableRelationship]:
    """
    Extract all foreign key relationships across the database.

    Args:
        db: Database session

    Returns:
        List of TableRelationship objects
    """
    query = text("""
        SELECT
            tc.table_name as from_table,
            kcu.column_name as from_column,
            ccu.table_name AS to_table,
            ccu.column_name AS to_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
            AND tc.table_schema = ccu.table_schema
        WHERE tc.table_schema = 'public'
        AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, kcu.column_name
    """)

    result = db.execute(query)
    relationships = []
    for row in result:
        relationships.append(TableRelationship(
            from_table=row.from_table,
            from_column=row.from_column,
            to_table=row.to_table,
            to_column=row.to_column,
            constraint_name=row.constraint_name
        ))

    logger.info(f"Retrieved {len(relationships)} foreign key relationships")
    return relationships


def get_complete_schema(db: Session) -> DatabaseSchema:
    """
    Retrieve complete database schema including all tables, columns, constraints, and relationships.

    Args:
        db: Database session

    Returns:
        DatabaseSchema object containing all schema information
    """
    logger.info("Retrieving complete database schema")

    # Get all tables
    tables_data = get_all_tables(db)

    # Build TableSchema objects for each table
    table_schemas = []
    for table_data in tables_data:
        table_name = table_data["table_name"]
        columns = get_table_columns(db, table_name)
        constraints = get_table_constraints(db, table_name)

        table_schema = TableSchema(
            name=table_name,
            type=table_data["table_type"],
            columns=columns,
            constraints=constraints
        )
        table_schemas.append(table_schema)

    # Get all relationships
    relationships = extract_relationships(db)

    schema = DatabaseSchema(
        tables=table_schemas,
        relationships=relationships
    )

    logger.info(f"Complete schema retrieved: {len(table_schemas)} tables, {len(relationships)} relationships")
    return schema


def get_table_schema(db: Session, table_name: str) -> Optional[TableSchema]:
    """
    Retrieve schema information for a specific table.

    Args:
        db: Database session
        table_name: Name of the table

    Returns:
        TableSchema object or None if table doesn't exist
    """
    # Check if table exists
    query = text("""
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = :table_name
    """)

    result = db.execute(query, {"table_name": table_name})
    row = result.fetchone()

    if not row:
        logger.warning(f"Table {table_name} not found in public schema")
        return None

    # Get columns and constraints
    columns = get_table_columns(db, table_name)
    constraints = get_table_constraints(db, table_name)

    table_schema = TableSchema(
        name=table_name,
        type=row.table_type,
        columns=columns,
        constraints=constraints
    )

    logger.info(f"Retrieved schema for table {table_name}")
    return table_schema


def get_table_relationships(db: Session) -> List[TableRelationship]:
    """
    Retrieve all foreign key relationships across the database.
    This is a convenience wrapper around extract_relationships.

    Args:
        db: Database session

    Returns:
        List of TableRelationship objects
    """
    return extract_relationships(db)


def get_reference_data(db: Session, data_type: str) -> ReferenceDataResponse:
    """
    Retrieve reference data from lookup tables.

    Args:
        db: Database session
        data_type: Type of reference data ("currencies", "account_types", "categories", "all")

    Returns:
        ReferenceDataResponse object

    Raises:
        ValueError: If data_type is invalid
    """
    valid_types = ["currencies", "account_types", "categories", "all"]
    if data_type not in valid_types:
        raise ValueError(f"Invalid data_type '{data_type}'. Must be one of: {', '.join(valid_types)}")

    result_data: Any = {}

    if data_type in ["currencies", "all"]:
        query = text("""
            SELECT currency_code, currency_name, currency_symbol, decimal_places, is_active
            FROM currencies
            WHERE is_active = TRUE
            ORDER BY currency_code
        """)
        result = db.execute(query)
        currencies = [dict(row._mapping) for row in result]
        if data_type == "all":
            result_data["currencies"] = currencies
        else:
            result_data = currencies

    if data_type in ["account_types", "all"]:
        query = text("""
            SELECT account_type_id, type_name, description, is_asset
            FROM account_types
            ORDER BY type_name
        """)
        result = db.execute(query)
        account_types = [dict(row._mapping) for row in result]
        if data_type == "all":
            result_data["account_types"] = account_types
        else:
            result_data = account_types

    if data_type in ["categories", "all"]:
        query = text("""
            SELECT category_id, category_name, category_group, category_type,
                   color_code, icon_name, is_active
            FROM categories
            WHERE is_active = TRUE
            ORDER BY category_group, category_name
        """)
        result = db.execute(query)
        categories = [dict(row._mapping) for row in result]
        if data_type == "all":
            result_data["categories"] = categories
        else:
            result_data = categories

    logger.info(f"Retrieved reference data for type: {data_type}")
    return ReferenceDataResponse(data_type=data_type, data=result_data)
