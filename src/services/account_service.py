"""
Account service layer implementing business logic for account operations.
Handles CRUD operations and filtering for accounts.
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func

from src.models.account import Account
from src.schemas.account import AccountCreate, AccountUpdate


def create_account(db: Session, account_data: AccountCreate) -> Account:
    """
    Create a new account.

    Args:
        db: Database session
        account_data: Account creation data

    Returns:
        Created account instance

    Raises:
        IntegrityError: If foreign key constraints are violated
    """
    account = Account(**account_data.model_dump(exclude_unset=True))
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_account(db: Session, account_id: int) -> Optional[Account]:
    """
    Get an account by ID.

    Args:
        db: Database session
        account_id: Account ID

    Returns:
        Account instance if found, None otherwise
    """
    return db.query(Account).filter(Account.account_id == account_id).first()


def list_accounts(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    account_type_id: Optional[int] = None,
    currency_code: Optional[str] = None,
    is_closed: Optional[bool] = None
) -> Tuple[List[Account], int]:
    """
    List accounts with optional filtering and pagination.

    Args:
        db: Database session
        limit: Maximum number of results
        offset: Number of results to skip
        account_type_id: Filter by account type ID
        currency_code: Filter by currency code
        is_closed: Filter by closed status

    Returns:
        Tuple of (list of accounts, total count)
    """
    query = db.query(Account)

    # Apply filters
    if account_type_id is not None:
        query = query.filter(Account.account_type_id == account_type_id)
    if currency_code is not None:
        query = query.filter(Account.currency_code == currency_code)
    if is_closed is not None:
        query = query.filter(Account.is_closed == is_closed)

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    accounts = query.offset(offset).limit(limit).all()

    return accounts, total


def update_account(
    db: Session,
    account_id: int,
    account_data: AccountUpdate,
    partial: bool = True
) -> Optional[Account]:
    """
    Update an existing account.

    Args:
        db: Database session
        account_id: Account ID to update
        account_data: Account update data
        partial: If True, only update provided fields (PATCH). If False, update all fields (PUT).

    Returns:
        Updated account instance if found, None otherwise

    Raises:
        IntegrityError: If foreign key constraints are violated
    """
    account = get_account(db, account_id)
    if not account:
        return None

    update_data = account_data.model_dump(exclude_unset=partial)
    for field, value in update_data.items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account_id: int) -> bool:
    """
    Delete an account.

    Args:
        db: Database session
        account_id: Account ID to delete

    Returns:
        True if account was deleted, False if not found

    Raises:
        IntegrityError: If account has associated transactions
    """
    account = get_account(db, account_id)
    if not account:
        return False

    db.delete(account)
    db.commit()
    return True
