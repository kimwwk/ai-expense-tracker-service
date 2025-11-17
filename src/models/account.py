"""
Account model representing the accounts table.
Maps to the existing 'accounts' table in the database.
"""
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Boolean, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Account(Base):
    """
    Account model representing financial accounts.

    Represents bank accounts, credit cards, cash, and other financial accounts.
    The current_balance is automatically maintained by database triggers.
    """
    __tablename__ = "accounts"

    # Primary Key
    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    account_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("account_types.account_type_id"), nullable=False
    )
    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    currency_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.currency_code"), nullable=False, default="USD"
    )
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0.00)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0.00)

    # Optional Fields
    account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    institution_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    opening_balance_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())

    # Timestamps (managed by database triggers)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    account_type: Mapped["AccountType"] = relationship("AccountType")
    currency: Mapped["Currency"] = relationship("Currency")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="account")
