"""
Transaction API router implementing REST endpoints for transaction management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.services import transaction_service
from src.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])


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
