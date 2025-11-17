"""
Category model representing the categories table.
Maps to the existing 'categories' table in the database.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Category(Base):
    """
    Category model for expense and income classification.

    Represents expense or income categories (groceries, salary, utilities, etc.)
    for organizing and analyzing transactions.
    """
    __tablename__ = "categories"

    # Primary Key
    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Optional Fields
    category_group: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color_code: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    icon_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="category")
