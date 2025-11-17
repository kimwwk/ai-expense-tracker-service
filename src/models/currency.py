"""
Currency model representing the currencies reference data table.
Maps to the existing 'currencies' table in the database.
"""
from typing import Optional
from sqlalchemy import String, SmallInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Currency(Base):
    """
    Currency reference data model.

    Represents supported currencies with ISO 4217 codes.
    This is read-only reference data seeded at database initialization.
    """
    __tablename__ = "currencies"

    # Primary Key
    currency_code: Mapped[str] = mapped_column(String(3), primary_key=True)

    # Required Fields
    currency_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Optional Fields
    currency_symbol: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    decimal_places: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
