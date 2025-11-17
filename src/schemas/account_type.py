"""
AccountType Pydantic schemas for API request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AccountTypeResponse(BaseModel):
    """
    Response schema for AccountType reference data.
    Used in GET /account-types and other endpoints that reference account types.
    """
    account_type_id: int
    type_name: str
    description: Optional[str]
    is_asset: bool

    model_config = ConfigDict(from_attributes=True)
