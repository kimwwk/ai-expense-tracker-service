"""
Reference data service layer for read-only reference tables.
Provides access to account types and currencies.
"""
from typing import List
from sqlalchemy.orm import Session

from src.models.account_type import AccountType
from src.models.currency import Currency


def list_account_types(db: Session) -> List[AccountType]:
    """
    List all account types.

    Args:
        db: Database session

    Returns:
        List of all account types
    """
    return db.query(AccountType).all()


def list_currencies(db: Session, active_only: bool = True) -> List[Currency]:
    """
    List all currencies, optionally filtered by active status.

    Args:
        db: Database session
        active_only: If True, only return active currencies

    Returns:
        List of currencies
    """
    query = db.query(Currency)
    if active_only:
        query = query.filter(Currency.is_active == True)
    return query.all()
