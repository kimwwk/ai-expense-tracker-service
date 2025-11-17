"""
Reference data API router for read-only reference tables.
Provides endpoints for account types and currencies.
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.services import reference_service
from src.schemas.account_type import AccountTypeResponse
from src.schemas.currency import CurrencyResponse

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get(
    "/account-types",
    response_model=List[AccountTypeResponse],
    summary="Get all account types"
)
def get_account_types(db: Session = Depends(get_db)):
    """
    Retrieve all account types.

    Returns a list of available account types (checking, savings, credit card, etc.)
    for use in account creation and filtering.

    This is read-only reference data seeded at database initialization.
    """
    account_types = reference_service.list_account_types(db)
    return account_types


@router.get(
    "/currencies",
    response_model=List[CurrencyResponse],
    summary="Get all currencies"
)
def get_currencies(
    active_only: bool = Query(True, description="Return only active currencies"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all supported currencies.

    Returns a list of available currencies (USD, GBP, CAD, etc.)
    for use in account and transaction creation.

    This is read-only reference data seeded at database initialization.

    **Parameters:**
    - **active_only**: If true (default), only return active currencies
    """
    currencies = reference_service.list_currencies(db, active_only=active_only)
    return currencies
