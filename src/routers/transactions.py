"""
Transaction API router implementing REST endpoints for transaction management.
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.services import transaction_service
from src.schemas.transaction import TransactionCreate, TransactionResponse
from src.schemas.common import PaginatedResponse, PaginationMetadata
from src.schemas.enums import TransactionType, TransactionStatus

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get(
    "",
    response_model=PaginatedResponse[TransactionResponse],
    summary="List transactions with filtering and pagination"
)
def list_transactions(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    payee_id: Optional[int] = Query(None, description="Filter by payee ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type (income/expense)"),
    status: Optional[TransactionStatus] = Query(None, description="Filter by transaction status"),
    start_date: Optional[date] = Query(None, description="Filter by transaction date >= start_date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by transaction date <= end_date (YYYY-MM-DD)"),
    sort: str = Query("transaction_date", description="Field to sort by (transaction_date, amount, created_at)"),
    order: str = Query("desc", description="Sort order (asc/desc)", regex="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results (1-100)"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    List and filter transactions with pagination support.

    **Filtering Options:**
    - **account_id**: Filter by specific account
    - **category_id**: Filter by specific category
    - **payee_id**: Filter by specific payee
    - **transaction_type**: Filter by type ('income' or 'expense')
    - **status**: Filter by status ('pending', 'cleared', 'reconciled', 'void')
    - **start_date**: Show transactions on or after this date
    - **end_date**: Show transactions on or before this date

    **Sorting:**
    - **sort**: Field to sort by (transaction_date, amount, created_at)
    - **order**: Sort direction ('asc' or 'desc')

    **Pagination:**
    - **limit**: Results per page (default: 50, max: 100)
    - **offset**: Number of results to skip (default: 0)

    Returns paginated list with metadata including total count.
    """
    # Validate sort field
    valid_sort_fields = ["transaction_date", "amount", "created_at"]
    if sort not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Invalid sort field: {sort}",
                    "details": {
                        "field": "sort",
                        "reason": f"must be one of: {', '.join(valid_sort_fields)}"
                    }
                }
            }
        )

    # Call service layer
    transactions, total = transaction_service.list_transactions(
        db=db,
        account_id=account_id,
        category_id=category_id,
        payee_id=payee_id,
        transaction_type=transaction_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        sort=sort,
        order=order,
        limit=limit,
        offset=offset
    )

    # Build paginated response
    return PaginatedResponse(
        data=transactions,
        pagination=PaginationMetadata(
            limit=limit,
            offset=offset,
            total=total
        )
    )


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction"
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new financial transaction (income or expense).

    **Note**: Transfer transactions are OUT OF SCOPE for this API.

    - **account_id**: Account for this transaction
    - **transaction_type**: Type of transaction ('income' or 'expense')
    - **amount**: Transaction amount (must be positive)
    - **currency_code**: 3-letter ISO currency code
    - **base_amount**: Amount in base currency (for multi-currency support)
    - **transaction_date**: Date of transaction (ISO 8601 format)
    - **status**: Transaction status (default: 'cleared')
    - **exchange_rate**: Exchange rate (default: 1.000000)
    - **payee_id**: Optional payee reference
    - **category_id**: Optional category reference
    - **description**: Optional description
    - **reference_number**: Optional reference/check number
    - **location**: Optional location
    - **notes**: Optional additional notes

    The account balance is automatically updated by database triggers.
    """
    try:
        transaction = transaction_service.create_transaction(db, transaction_data)
        return transaction
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
                            "reason": "account_id, category_id, payee_id, or currency_code does not exist"
                        }
                    }
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Failed to create transaction",
                    "details": {"reason": str(e)}
                }
            }
        )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction by ID"
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific transaction by its ID.

    Returns the transaction details including all fields.
    """
    transaction = transaction_service.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Transaction with ID {transaction_id} not found"
                }
            }
        )
    return transaction
