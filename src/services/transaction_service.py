"""
Transaction service layer implementing business logic for transaction operations.
Handles CRUD operations for transactions.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.transaction import Transaction
from src.schemas.transaction import TransactionCreate, TransactionUpdate


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
