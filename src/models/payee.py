"""
Payee model representing the payees table.
Maps to the existing 'payees' table in the database.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Payee(Base):
    """
    Payee model for transaction parties.

    Represents merchants, vendors, or entities involved in transactions
    (e.g., grocery stores, employers, service providers).
    """
    __tablename__ = "payees"

    # Primary Key
    payee_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    payee_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Optional Fields
    default_category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.category_id"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    default_category: Mapped[Optional["Category"]] = relationship("Category")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="payee")
