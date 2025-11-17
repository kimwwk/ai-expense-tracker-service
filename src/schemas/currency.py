"""
Currency Pydantic schemas for API request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CurrencyResponse(BaseModel):
    """
    Response schema for Currency reference data.
    Used in GET /currencies and other endpoints that reference currencies.
    """
    currency_code: str
    currency_name: str
    currency_symbol: Optional[str]
    decimal_places: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
