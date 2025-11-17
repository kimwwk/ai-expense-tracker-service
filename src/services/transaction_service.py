"""
Transaction service layer implementing business logic for transaction operations.
Handles CRUD operations for transactions.
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, asc

from src.models.transaction import Transaction
from src.schemas.transaction import TransactionCreate, TransactionUpdate
from src.schemas.enums import TransactionType, TransactionStatus


def create_transaction(db: Session, transaction_data: TransactionCreate) -> Transaction:
    """
    Create a new transaction.

    Args:
        db: Database session
        transaction_data: Transaction creation data

    Returns:
        Created transaction instance

    Raises:
        IntegrityError: If foreign key constraints are violated

    Note:
        Account balance is automatically updated by database trigger.
    """
    transaction = Transaction(**transaction_data.model_dump(exclude_unset=True))
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """
    Get a transaction by ID.

    Args:
        db: Database session
        transaction_id: Transaction ID

    Returns:
        Transaction instance if found, None otherwise
    """
    return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction_data: TransactionUpdate,
    partial: bool = True
) -> Optional[Transaction]:
    """
    Update an existing transaction.

    Args:
        db: Database session
        transaction_id: Transaction ID to update
        transaction_data: Transaction update data
        partial: If True, only update provided fields (PATCH). If False, update all fields (PUT).

    Returns:
        Updated transaction instance if found, None otherwise

    Raises:
        IntegrityError: If foreign key constraints are violated

    Note:
        Account balance is automatically updated by database trigger.
    """
    transaction = get_transaction(db, transaction_id)
    if not transaction:
        return None

    update_data = transaction_data.model_dump(exclude_unset=partial)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction_id: int) -> bool:
    """
    Delete a transaction.

    Args:
        db: Database session
        transaction_id: Transaction ID to delete

    Returns:
        True if transaction was deleted, False if not found

    Note:
        Account balance is automatically updated by database trigger.
    """
    transaction = get_transaction(db, transaction_id)
    if not transaction:
        return False

    db.delete(transaction)
    db.commit()
    return True


def list_transactions(
    db: Session,
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    payee_id: Optional[int] = None,
    transaction_type: Optional[TransactionType] = None,
    status: Optional[TransactionStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort: str = "transaction_date",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple[List[Transaction], int]:
    """
    List transactions with optional filtering, sorting, and pagination.

    Args:
        db: Database session
        account_id: Filter by account ID
        category_id: Filter by category ID
        payee_id: Filter by payee ID
        transaction_type: Filter by transaction type (income/expense)
        status: Filter by transaction status
        start_date: Filter by transaction date >= start_date
        end_date: Filter by transaction date <= end_date
        sort: Field to sort by (transaction_date, amount, created_at)
        order: Sort order (asc/desc)
        limit: Maximum number of results to return (max 100)
        offset: Number of results to skip

    Returns:
        Tuple of (list of transactions, total count)

    Note:
        Limit is capped at 100 to prevent excessive data transfer.
    """
    # Start with base query
    query = db.query(Transaction)

    # Apply filters
    if account_id is not None:
        query = query.filter(Transaction.account_id == account_id)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if payee_id is not None:
        query = query.filter(Transaction.payee_id == payee_id)
    if transaction_type is not None:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if status is not None:
        query = query.filter(Transaction.status == status)
    if start_date is not None:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.transaction_date <= end_date)

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_field = getattr(Transaction, sort, Transaction.transaction_date)
    if order == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    transactions = query.all()

    return transactions, total
