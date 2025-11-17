"""
AccountType model representing the account_types reference data table.
Maps to the existing 'account_types' table in the database.
"""
from typing import Optional
from sqlalchemy import String, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class AccountType(Base):
    """
    AccountType reference data model.

    Represents types of financial accounts (checking, savings, credit card, etc.).
    This is read-only reference data seeded at database initialization.
    """
    __tablename__ = "account_types"

    # Primary Key
    account_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required Fields
    type_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    is_asset: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Optional Fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
