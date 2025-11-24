"""
Database schema discovery API router.
Provides endpoints for exploring database structure, tables, relationships, and reference data.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.database import get_db
from src.schemas.schema import (
    DatabaseSchema,
    TableSchema,
    TableRelationship,
    ReferenceDataResponse
)
from src.services import schema_service

# Initialize logger
logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/schema", tags=["schema"])


@router.get(
    "",
    response_model=DatabaseSchema,
    summary="Get complete database schema"
)
def get_database_schema(db: Session = Depends(get_db)):
    """Get complete database schema with all tables, columns, constraints, and relationships."""
    try:
        logger.info("Retrieving complete database schema")
        schema = schema_service.get_complete_schema(db)
        logger.info(f"Successfully retrieved schema: {len(schema.tables)} tables, {len(schema.relationships)} relationships")
        return schema
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving schema: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DATABASE_ERROR", "message": "Failed to retrieve database schema"}}
        )
    except Exception as e:
        logger.error(f"Unexpected error while retrieving schema: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}
        )


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


@router.get(
    "/tables/{table_name}",
    response_model=TableSchema,
    summary="Get schema for specific table"
)
def get_table_schema_endpoint(table_name: str, db: Session = Depends(get_db)):
    """Get detailed schema information for a specific table."""
    try:
        logger.info(f"Retrieving schema for table: {table_name}")
        table_schema = schema_service.get_table_schema(db, table_name)

        if table_schema is None:
            logger.warning(f"Table {table_name} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Table '{table_name}' not found in public schema",
                        "details": {"table_name": table_name, "schema": "public"}
                    }
                }
            )

        logger.info(f"Successfully retrieved schema for table {table_name}")
        return table_schema
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DATABASE_ERROR", "message": "Failed to retrieve table schema"}}
        )


@router.get(
    "/relationships",
    response_model=List[TableRelationship],
    summary="Get all foreign key relationships"
)
def get_relationships_endpoint(db: Session = Depends(get_db)):
    """Get all foreign key relationships across the database."""
    try:
        logger.info("Retrieving table relationships")
        relationships = schema_service.get_table_relationships(db)
        logger.info(f"Successfully retrieved {len(relationships)} relationships")
        return relationships
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DATABASE_ERROR", "message": "Failed to retrieve relationships"}}
        )


@router.get(
    "/reference-data",
    response_model=ReferenceDataResponse,
    summary="Get reference data values"
)
def get_reference_data_endpoint(
    type: str = Query(..., description="Type: currencies, account_types, categories, or all"),
    db: Session = Depends(get_db)
):
    """Get reference data from lookup tables."""
    valid_types = ["currencies", "account_types", "categories", "all"]

    if type not in valid_types:
        logger.warning(f"Invalid reference data type: {type}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": f"Invalid type '{type}'",
                    "details": {"parameter": "type", "provided_value": type, "valid_values": valid_types}
                }
            }
        )

    try:
        logger.info(f"Retrieving reference data for type: {type}")
        reference_data = schema_service.get_reference_data(db, type)
        logger.info(f"Successfully retrieved reference data for type {type}")
        return reference_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "INVALID_PARAMETER", "message": str(e)}}
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DATABASE_ERROR", "message": "Failed to retrieve reference data"}}
        )
