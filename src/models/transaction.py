"""
Transaction model representing the transactions table.
Maps to the existing 'transactions' table in the database.
"""
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Date, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Transaction(Base):
    """
    Transaction model for financial transactions.

    Represents income and expense transactions.
    Note: Transfer transactions (transaction_type='transfer') are OUT OF SCOPE for this API.
    Account balances are automatically maintained by database triggers.
    """
    __tablename__ = "transactions"

    # Primary Key
    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.account_id"), nullable=False
    )
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.currency_code"), nullable=False
    )
    base_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="cleared")

    # Optional Fields
    payee_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("payees.payee_id"), nullable=True
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.category_id"), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False, default=1.000000)
    transfer_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounts.account_id"), nullable=True
    )
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps (managed by database triggers)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    account: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="transactions")
    payee: Mapped[Optional["Payee"]] = relationship("Payee", back_populates="transactions")
    currency: Mapped["Currency"] = relationship("Currency")
