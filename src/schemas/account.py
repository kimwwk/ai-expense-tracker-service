"""
Account Pydantic schemas for API request/response validation.
"""
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class AccountCreate(BaseModel):
    """
    Request schema for creating a new account.
    Only includes fields that can be set during creation.
    """
    # Required fields
    account_type_id: int
    account_name: str = Field(min_length=1, max_length=100)
    currency_code: str = Field(pattern=r"^[A-Z]{3}$", default="USD")
    opening_balance: Decimal = Field(default=Decimal("0.00"), max_digits=15, decimal_places=2)

    # Optional fields with defaults
    is_closed: bool = False
    opening_balance_date: Optional[date] = None  # Defaults to current date in DB

    # Optional fields
    account_number: Optional[str] = Field(None, max_length=50)
    institution_name: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    notes: Optional[str] = None


class AccountUpdate(BaseModel):
    """
    Request schema for updating an existing account.
    All fields are optional to support partial updates (PATCH).
    Note: opening_balance and opening_balance_date should not be updated.
    """
    account_type_id: Optional[int] = None
    account_name: Optional[str] = Field(None, min_length=1, max_length=100)
    currency_code: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    account_number: Optional[str] = Field(None, max_length=50)
    institution_name: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    is_closed: Optional[bool] = None
    notes: Optional[str] = None


class AccountResponse(BaseModel):
    """
    Response schema for account data.
    Includes all fields including read-only current_balance maintained by triggers.
    """
    account_id: int
    account_type_id: int
    account_name: str
    account_number: Optional[str]
    institution_name: Optional[str]
    currency_code: str
    opening_balance: Decimal
    current_balance: Decimal  # Read-only, maintained by database triggers
    credit_limit: Optional[Decimal]
    is_closed: bool
    notes: Optional[str]
    opening_balance_date: date
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
