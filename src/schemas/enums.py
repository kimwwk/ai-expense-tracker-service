"""
Enum definitions for transaction types, statuses, and category types.
These match the database CHECK constraints.
"""
from enum import Enum


class TransactionType(str, Enum):
    """
    Transaction type enumeration.
    Matches database CHECK constraint on transactions.transaction_type.

    Note: 'transfer' type exists in database but is OUT OF SCOPE for this API.
    Only 'income' and 'expense' are supported.
    """

    INCOME = "income"
    EXPENSE = "expense"
    # TRANSFER = "transfer"  # Out of scope for this API


class TransactionStatus(str, Enum):
    """
    Transaction status enumeration.
    Matches database CHECK constraint on transactions.status.
    """

    PENDING = "pending"
    CLEARED = "cleared"
    RECONCILED = "reconciled"
    VOID = "void"


class CategoryType(str, Enum):
    """
    Category type enumeration.
    Matches database CHECK constraint on categories.category_type.
    """

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
