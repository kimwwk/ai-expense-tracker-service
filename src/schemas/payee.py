"""
Payee Pydantic schemas for API request/response validation.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PayeeResponse(BaseModel):
    """
    Response schema for Payee data.
    Used when payees are referenced in transactions or listed.
    """
    payee_id: int
    payee_name: str
    default_category_id: Optional[int]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PayeeCreate(BaseModel):
    """
    Request schema for creating a new payee.
    """
    # Required fields
    payee_name: str = Field(min_length=1, max_length=100)

    # Optional fields
    default_category_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool = True


class PayeeUpdate(BaseModel):
    """
    Request schema for updating a payee.
    All fields are optional to support partial updates.
    """
    payee_name: Optional[str] = Field(None, min_length=1, max_length=100)
    default_category_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
