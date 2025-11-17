"""
Payee service layer implementing business logic for payee operations.
Handles CRUD operations for payees.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.payee import Payee
from src.schemas.payee import PayeeCreate, PayeeUpdate


def create_payee(db: Session, payee_data: PayeeCreate) -> Payee:
    """
    Create a new payee.

    Args:
        db: Database session
        payee_data: Payee creation data

    Returns:
        Created payee instance

    Raises:
        IntegrityError: If constraints are violated (e.g., duplicate name, invalid category_id)
    """
    payee = Payee(**payee_data.model_dump(exclude_unset=True))
    db.add(payee)
    db.commit()
    db.refresh(payee)
    return payee


def get_payee(db: Session, payee_id: int) -> Optional[Payee]:
    """
    Get a payee by ID.

    Args:
        db: Database session
        payee_id: Payee ID

    Returns:
        Payee instance if found, None otherwise
    """
    return db.query(Payee).filter(Payee.payee_id == payee_id).first()


def list_payees(
    db: Session,
    is_active: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[List[Payee], int]:
    """
    List payees with optional filtering and pagination.

    Args:
        db: Database session
        is_active: Filter by active status
        limit: Maximum number of results to return (default 100)
        offset: Number of results to skip

    Returns:
        Tuple of (list of payees, total count)
    """
    query = db.query(Payee)

    # Apply filters
    if is_active is not None:
        query = query.filter(Payee.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply ordering (alphabetical by name)
    query = query.order_by(Payee.payee_name)

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    payees = query.all()

    return payees, total


def update_payee(
    db: Session,
    payee_id: int,
    payee_data: PayeeUpdate,
    partial: bool = True
) -> Optional[Payee]:
    """
    Update an existing payee.

    Args:
        db: Database session
        payee_id: Payee ID to update
        payee_data: Payee update data
        partial: If True, only update provided fields (PATCH). If False, update all fields (PUT).

    Returns:
        Updated payee instance if found, None otherwise

    Raises:
        IntegrityError: If constraints are violated (e.g., invalid default_category_id)
    """
    payee = get_payee(db, payee_id)
    if not payee:
        return None

    update_data = payee_data.model_dump(exclude_unset=partial)
    for field, value in update_data.items():
        setattr(payee, field, value)

    db.commit()
    db.refresh(payee)
    return payee


def delete_payee(db: Session, payee_id: int) -> bool:
    """
    Delete a payee.

    Args:
        db: Database session
        payee_id: Payee ID to delete

    Returns:
        True if payee was deleted, False if not found

    Note:
        May fail if payee is referenced by transactions (foreign key constraint).
    """
    payee = get_payee(db, payee_id)
    if not payee:
        return False

    db.delete(payee)
    db.commit()
    return True
