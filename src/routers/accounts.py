"""
Account API router implementing REST endpoints for account management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.services import account_service
from src.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from src.schemas.common import PaginatedResponse, PaginationMetadata

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account"
)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new financial account.

    - **account_type_id**: Type of account (checking, savings, etc.)
    - **account_name**: Name/label for the account
    - **currency_code**: 3-letter ISO currency code (default: USD)
    - **opening_balance**: Initial balance (default: 0.00)
    - **opening_balance_date**: Date of opening balance (defaults to today)
    - **account_number**: Optional account number
    - **institution_name**: Optional bank/institution name
    - **credit_limit**: Optional credit limit for credit cards
    - **is_closed**: Whether account is closed (default: false)
    - **notes**: Optional notes
    """
    try:
        account = account_service.create_account(db, account_data)
        return account
    except IntegrityError as e:
        db.rollback()
        # Check for foreign key violation
        if "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid foreign key reference",
                        "details": {
                            "reason": "account_type_id or currency_code does not exist"
                        }
                    }
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Failed to create account",
                    "details": {"reason": str(e)}
                }
            }
        )


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Get account by ID"
)
def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific account by its ID.

    Returns the account details including current balance (maintained by database triggers).
    """
    account = account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Account with ID {account_id} not found"
                }
            }
        )
    return account


@router.get(
    "",
    response_model=PaginatedResponse[AccountResponse],
    summary="List accounts with optional filtering"
)
def list_accounts(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    account_type_id: Optional[int] = Query(None, description="Filter by account type ID"),
    currency_code: Optional[str] = Query(None, description="Filter by currency code"),
    is_closed: Optional[bool] = Query(None, description="Filter by closed status"),
    db: Session = Depends(get_db)
):
    """
    List all accounts with optional filtering and pagination.

    **Filters:**
    - **account_type_id**: Filter by account type
    - **currency_code**: Filter by currency
    - **is_closed**: Filter by closed status

    **Pagination:**
    - **limit**: Max results (1-100, default 50)
    - **offset**: Skip N results (default 0)
    """
    accounts, total = account_service.list_accounts(
        db,
        limit=limit,
        offset=offset,
        account_type_id=account_type_id,
        currency_code=currency_code,
        is_closed=is_closed
    )

    return PaginatedResponse(
        data=accounts,
        pagination=PaginationMetadata(
            limit=limit,
            offset=offset,
            total=total
        )
    )


@router.put(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Update account (full update)"
)
def update_account_full(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an account with full replacement.

    In practice, this behaves like PATCH - only provided fields are updated.
    Note: opening_balance and opening_balance_date cannot be updated.
    """
    try:
        account = account_service.update_account(db, account_id, account_data, partial=True)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Account with ID {account_id} not found"
                    }
                }
            )
        return account
    except IntegrityError as e:
        db.rollback()
        if "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid foreign key reference",
                        "details": {
                            "reason": "account_type_id or currency_code does not exist"
                        }
                    }
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Failed to update account"
                }
            }
        )


@router.patch(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Update account (partial update)"
)
def update_account_partial(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an account with partial updates.

    Only provided fields will be updated. Omitted fields remain unchanged.
    Note: opening_balance and opening_balance_date cannot be updated.
    """
    try:
        account = account_service.update_account(db, account_id, account_data, partial=True)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Account with ID {account_id} not found"
                    }
                }
            )
        return account
    except IntegrityError as e:
        db.rollback()
        if "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid foreign key reference",
                        "details": {
                            "reason": "account_type_id or currency_code does not exist"
                        }
                    }
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Failed to update account"
                }
            }
        )


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an account"
)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an account.

    Returns 204 No Content on success, 404 if account not found.
    Will fail with 422 if account has associated transactions.
    """
    try:
        deleted = account_service.delete_account(db, account_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Account with ID {account_id} not found"
                    }
                }
            )
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Cannot delete account with existing transactions",
                    "details": {
                        "reason": "Foreign key constraint violation"
                    }
                }
            }
        )
