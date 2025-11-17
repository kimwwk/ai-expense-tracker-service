"""
Category API router implementing REST endpoints for category management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.services import category_service
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.schemas.common import PaginatedResponse, PaginationMetadata

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=PaginatedResponse[CategoryResponse],
    summary="List categories with filtering and pagination"
)
def list_categories(
    category_type: Optional[str] = Query(None, description="Filter by category type (income/expense/transfer)"),
    category_group: Optional[str] = Query(None, description="Filter by category group"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of results (1-200)"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    List and filter categories with pagination support.

    **Filtering Options:**
    - **category_type**: Filter by type ('income', 'expense', 'transfer')
    - **category_group**: Filter by category group
    - **is_active**: Filter by active status (true/false)

    **Pagination:**
    - **limit**: Results per page (default: 100, max: 200)
    - **offset**: Number of results to skip (default: 0)

    Returns paginated list with metadata including total count.
    Categories are sorted alphabetically by name.
    """
    categories, total = category_service.list_categories(
        db=db,
        category_type=category_type,
        category_group=category_group,
        is_active=is_active,
        limit=limit,
        offset=offset
    )

    return PaginatedResponse(
        data=categories,
        pagination=PaginationMetadata(
            limit=limit,
            offset=offset,
            total=total
        )
    )


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category"
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new expense/income category.

    - **category_name**: Category name (required, 1-100 characters)
    - **category_type**: Type of category ('income', 'expense', 'transfer')
    - **category_group**: Optional group name for organizing categories
    - **color_code**: Optional hex color code (e.g., '#FF5733')
    - **icon_name**: Optional icon identifier
    - **is_active**: Whether category is active (default: true)
    """
    try:
        category = category_service.create_category(db, category_data)
        return category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Failed to create category",
                    "details": {"reason": "Possible duplicate category name or constraint violation"}
                }
            }
        )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category by ID"
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific category by its ID.

    Returns the category details including all fields.
    """
    category = category_service.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Category with ID {category_id} not found"
                }
            }
        )
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update category (full update)"
)
def update_category_put(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Fully update a category (PUT).

    All fields in the request will be updated.
    """
    try:
        category = category_service.update_category(db, category_id, category_data, partial=False)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Category with ID {category_id} not found"
                    }
                }
            )
        return category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Failed to update category",
                    "details": {"reason": str(e)}
                }
            }
        )


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update category (partial update)"
)
def update_category_patch(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Partially update a category (PATCH).

    Only provided fields will be updated.
    """
    try:
        category = category_service.update_category(db, category_id, category_data, partial=True)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Category with ID {category_id} not found"
                    }
                }
            )
        return category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Failed to update category",
                    "details": {"reason": str(e)}
                }
            }
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a category by ID.

    Note: Deletion will fail if category is referenced by transactions.
    """
    try:
        success = category_service.delete_category(db, category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Category with ID {category_id} not found"
                    }
                }
            )
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "CONFLICT",
                    "message": "Cannot delete category",
                    "details": {"reason": "Category is referenced by existing transactions"}
                }
            }
        )
