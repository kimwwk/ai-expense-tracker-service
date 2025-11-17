"""
Transaction Pydantic schemas for API request/response validation.
"""
from typing import Optional, Literal
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class TransactionCreate(BaseModel):
    """
    Request schema for creating a new transaction.
    Only supports 'income' and 'expense' types. Transfer transactions are OUT OF SCOPE.
    """
    # Required fields
    account_id: int
    transaction_type: Literal["income", "expense"]  # NOTE: 'transfer' is OUT OF SCOPE
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    currency_code: str = Field(pattern=r"^[A-Z]{3}$")
    base_amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)
    transaction_date: date

    # Optional fields with defaults
    status: Optional[Literal["pending", "cleared", "reconciled", "void"]] = "cleared"
    exchange_rate: Optional[Decimal] = Field(Decimal("1.000000"), max_digits=10, decimal_places=6)

    # Optional fields
    payee_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=255)
    reference_number: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    """
    Request schema for updating a transaction.
    All fields are optional to support partial updates (PATCH).
    """
    account_id: Optional[int] = None
    transaction_type: Optional[Literal["income", "expense"]] = None
    amount: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)
    currency_code: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    base_amount: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)
    transaction_date: Optional[date] = None
    status: Optional[Literal["pending", "cleared", "reconciled", "void"]] = None
    exchange_rate: Optional[Decimal] = Field(None, max_digits=10, decimal_places=6)
    payee_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=255)
    reference_number: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    """
    Response schema for transaction data.
    Includes all fields including read-only transfer_account_id (OUT OF SCOPE for create/update).
    """
    transaction_id: int
    account_id: int
    transaction_type: str
    amount: Decimal
    currency_code: str
    base_amount: Decimal
    transaction_date: date
    status: str
    exchange_rate: Decimal
    payee_id: Optional[int]
    category_id: Optional[int]
    description: Optional[str]
    reference_number: Optional[str]
    transfer_account_id: Optional[int]  # Exposed but read-only (no create/update for transfers)
    location: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
