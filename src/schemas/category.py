"""
Category Pydantic schemas for API request/response validation.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class CategoryResponse(BaseModel):
    """
    Response schema for Category data.
    Used when categories are referenced in transactions or listed.
    """
    category_id: int
    category_name: str
    category_type: str
    category_group: Optional[str]
    color_code: Optional[str]
    icon_name: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    """
    Request schema for creating a new category.
    """
    # Required fields
    category_name: str = Field(min_length=1, max_length=100)
    category_type: Literal["income", "expense", "transfer"]

    # Optional fields
    category_group: Optional[str] = Field(None, max_length=50)
    color_code: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")  # Hex color
    icon_name: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class CategoryUpdate(BaseModel):
    """
    Request schema for updating a category.
    All fields are optional to support partial updates.
    """
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_type: Optional[Literal["income", "expense", "transfer"]] = None
    category_group: Optional[str] = Field(None, max_length=50)
    color_code: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
