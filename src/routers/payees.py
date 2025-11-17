"""
Payee API router implementing REST endpoints for payee management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.services import payee_service
from src.schemas.payee import PayeeCreate, PayeeUpdate, PayeeResponse
from src.schemas.common import PaginatedResponse, PaginationMetadata

router = APIRouter(prefix="/payees", tags=["payees"])


@router.get(
    "",
    response_model=PaginatedResponse[PayeeResponse],
    summary="List payees with filtering and pagination"
)
def list_payees(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of results (1-200)"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    List and filter payees with pagination support.

    **Filtering Options:**
    - **is_active**: Filter by active status (true/false)

    **Pagination:**
    - **limit**: Results per page (default: 100, max: 200)
    - **offset**: Number of results to skip (default: 0)

    Returns paginated list with metadata including total count.
    Payees are sorted alphabetically by name.
    """
    payees, total = payee_service.list_payees(
        db=db,
        is_active=is_active,
        limit=limit,
        offset=offset
    )

    return PaginatedResponse(
        data=payees,
        pagination=PaginationMetadata(
            limit=limit,
            offset=offset,
            total=total
        )
    )


@router.post(
    "",
    response_model=PayeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new payee"
)
def create_payee(
    payee_data: PayeeCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new payee for transactions.

    - **payee_name**: Payee name (required, 1-100 characters)
    - **default_category_id**: Optional default category for this payee
    - **notes**: Optional notes about the payee
    - **is_active**: Whether payee is active (default: true)
    """
    try:
        payee = payee_service.create_payee(db, payee_data)
        return payee
    except IntegrityError as e:
        db.rollback()
        # Check for foreign key violation
        if "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid default_category_id",
                        "details": {"reason": "Category does not exist"}
                    }
                }
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Failed to create payee",
                    "details": {"reason": "Possible duplicate payee name or constraint violation"}
                }
            }
        )


@router.get(
    "/{payee_id}",
    response_model=PayeeResponse,
    summary="Get payee by ID"
)
def get_payee(
    payee_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific payee by its ID.

    Returns the payee details including all fields.
    """
    payee = payee_service.get_payee(db, payee_id)
    if not payee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Payee with ID {payee_id} not found"
                }
            }
        )
    return payee


@router.put(
    "/{payee_id}",
    response_model=PayeeResponse,
    summary="Update payee (full update)"
)
def update_payee_put(
    payee_id: int,
    payee_data: PayeeUpdate,
    db: Session = Depends(get_db)
):
    """
    Fully update a payee (PUT).

    All fields in the request will be updated.
    """
    try:
        payee = payee_service.update_payee(db, payee_id, payee_data, partial=False)
        if not payee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Payee with ID {payee_id} not found"
                    }
                }
            )
        return payee
    except IntegrityError as e:
        db.rollback()
        if "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid default_category_id",
                        "details": {"reason": "Category does not exist"}
                    }
                }
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Failed to update payee",
                    "details": {"reason": str(e)}
                }
            }
        )


@router.patch(
    "/{payee_id}",
    response_model=PayeeResponse,
    summary="Update payee (partial update)"
)
def update_payee_patch(
    payee_id: int,
    payee_data: PayeeUpdate,
    db: Session = Depends(get_db)
):
    """
    Partially update a payee (PATCH).

    Only provided fields will be updated.
    """
    try:
        payee = payee_service.update_payee(db, payee_id, payee_data, partial=True)
        if not payee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Payee with ID {payee_id} not found"
                    }
                }
            )
        return payee
    except IntegrityError as e:
        db.rollback()
        if "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid default_category_id",
                        "details": {"reason": "Category does not exist"}
                    }
                }
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Failed to update payee",
                    "details": {"reason": str(e)}
                }
            }
        )


@router.delete(
    "/{payee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete payee"
)
def delete_payee(
    payee_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a payee by ID.

    Note: Deletion will fail if payee is referenced by transactions.
    """
    try:
        success = payee_service.delete_payee(db, payee_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Payee with ID {payee_id} not found"
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
                    "message": "Cannot delete payee",
                    "details": {"reason": "Payee is referenced by existing transactions"}
                }
            }
        )
