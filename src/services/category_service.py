"""
Category service layer implementing business logic for category operations.
Handles CRUD operations for categories.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.category import Category
from src.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    """
    Create a new category.

    Args:
        db: Database session
        category_data: Category creation data

    Returns:
        Created category instance

    Raises:
        IntegrityError: If constraints are violated (e.g., duplicate name)
    """
    category = Category(**category_data.model_dump(exclude_unset=True))
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """
    Get a category by ID.

    Args:
        db: Database session
        category_id: Category ID

    Returns:
        Category instance if found, None otherwise
    """
    return db.query(Category).filter(Category.category_id == category_id).first()


def list_categories(
    db: Session,
    category_type: Optional[str] = None,
    category_group: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[List[Category], int]:
    """
    List categories with optional filtering and pagination.

    Args:
        db: Database session
        category_type: Filter by category type (income/expense/transfer)
        category_group: Filter by category group
        is_active: Filter by active status
        limit: Maximum number of results to return (default 100)
        offset: Number of results to skip

    Returns:
        Tuple of (list of categories, total count)
    """
    query = db.query(Category)

    # Apply filters
    if category_type is not None:
        query = query.filter(Category.category_type == category_type)
    if category_group is not None:
        query = query.filter(Category.category_group == category_group)
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply ordering (alphabetical by name)
    query = query.order_by(Category.category_name)

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    categories = query.all()

    return categories, total


def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate,
    partial: bool = True
) -> Optional[Category]:
    """
    Update an existing category.

    Args:
        db: Database session
        category_id: Category ID to update
        category_data: Category update data
        partial: If True, only update provided fields (PATCH). If False, update all fields (PUT).

    Returns:
        Updated category instance if found, None otherwise

    Raises:
        IntegrityError: If constraints are violated
    """
    category = get_category(db, category_id)
    if not category:
        return None

    update_data = category_data.model_dump(exclude_unset=partial)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """
    Delete a category.

    Args:
        db: Database session
        category_id: Category ID to delete

    Returns:
        True if category was deleted, False if not found

    Note:
        May fail if category is referenced by transactions (foreign key constraint).
    """
    category = get_category(db, category_id)
    if not category:
        return False

    db.delete(category)
    db.commit()
    return True
