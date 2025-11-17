"""
Unit tests for transaction service business logic.
Tests CRUD operations and list/filter functionality.
"""
from datetime import date, datetime
from decimal import Decimal
import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from src.services.transaction_service import (
    create_transaction,
    get_transaction,
    update_transaction,
    delete_transaction,
    list_transactions
)
from src.models.transaction import Transaction
from src.schemas.transaction import TransactionCreate, TransactionUpdate
from src.schemas.enums import TransactionType, TransactionStatus


class TestListTransactions:
    """Test cases for list_transactions function with filtering and pagination."""

    def test_list_transactions_no_filters(self):
        """Test listing transactions without any filters."""
        # Setup mock database session
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        # Create mock transactions
        mock_transactions = [
            Transaction(
                transaction_id=1,
                account_id=1,
                transaction_type="expense",
                amount=Decimal("100.00"),
                transaction_date=date(2024, 1, 1)
            ),
            Transaction(
                transaction_id=2,
                account_id=1,
                transaction_type="income",
                amount=Decimal("200.00"),
                transaction_date=date(2024, 1, 2)
            ),
        ]

        # Mock query chain
        mock_query.count.return_value = 2
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_transactions

        # Call function
        transactions, total = list_transactions(mock_db)

        # Assertions
        assert total == 2
        assert len(transactions) == 2
        assert transactions[0].transaction_id == 1
        assert transactions[1].transaction_id == 2

    def test_list_transactions_with_account_filter(self):
        """Test filtering transactions by account_id."""
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        mock_transactions = [
            Transaction(
                transaction_id=1,
                account_id=5,
                transaction_type="expense",
                amount=Decimal("100.00"),
                transaction_date=date(2024, 1, 1)
            ),
        ]

        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_transactions

        transactions, total = list_transactions(mock_db, account_id=5)

        assert total == 1
        assert len(transactions) == 1
        assert transactions[0].account_id == 5

    def test_list_transactions_with_date_range(self):
        """Test filtering transactions by date range."""
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        mock_transactions = [
            Transaction(
                transaction_id=1,
                account_id=1,
                transaction_type="expense",
                amount=Decimal("100.00"),
                transaction_date=date(2024, 1, 15)
            ),
        ]

        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_transactions

        transactions, total = list_transactions(
            mock_db,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )

        assert total == 1
        assert len(transactions) == 1
        assert transactions[0].transaction_date == date(2024, 1, 15)

    def test_list_transactions_with_transaction_type_filter(self):
        """Test filtering by transaction type."""
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        mock_transactions = [
            Transaction(
                transaction_id=1,
                account_id=1,
                transaction_type="income",
                amount=Decimal("500.00"),
                transaction_date=date(2024, 1, 1)
            ),
        ]

        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_transactions

        transactions, total = list_transactions(
            mock_db,
            transaction_type=TransactionType.INCOME
        )

        assert total == 1
        assert transactions[0].transaction_type == "income"

    def test_list_transactions_with_status_filter(self):
        """Test filtering by transaction status."""
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        mock_transactions = [
            Transaction(
                transaction_id=1,
                account_id=1,
                transaction_type="expense",
                amount=Decimal("100.00"),
                transaction_date=date(2024, 1, 1),
                status="pending"
            ),
        ]

        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_transactions

        transactions, total = list_transactions(
            mock_db,
            status=TransactionStatus.PENDING
        )

        assert total == 1
        assert transactions[0].status == "pending"

    def test_list_transactions_pagination(self):
        """Test pagination with limit and offset."""
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        # Simulate 10 total transactions, returning 5 at offset 5
        mock_transactions = [
            Transaction(
                transaction_id=i,
                account_id=1,
                transaction_type="expense",
                amount=Decimal("100.00"),
                transaction_date=date(2024, 1, 1)
            )
            for i in range(6, 11)  # IDs 6-10
        ]

        mock_query.count.return_value = 10
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_transactions

        transactions, total = list_transactions(
            mock_db,
            limit=5,
            offset=5
        )

        assert total == 10
        assert len(transactions) == 5
        assert transactions[0].transaction_id == 6

    def test_list_transactions_sorting_asc(self):
        """Test sorting transactions in ascending order."""
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        mock_transactions = [
            Transaction(
                transaction_id=1,
                account_id=1,
                transaction_type="expense",
                amount=Decimal("50.00"),
                transaction_date=date(2024, 1, 1)
            ),
            Transaction(
                transaction_id=2,
                account_id=1,
                transaction_type="expense",
                amount=Decimal("100.00"),
                transaction_date=date(2024, 1, 2)
            ),
        ]

        mock_query.count.return_value = 2
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_transactions

        transactions, total = list_transactions(
            mock_db,
            sort="amount",
            order="asc"
        )

        assert total == 2
        assert transactions[0].amount == Decimal("50.00")
        assert transactions[1].amount == Decimal("100.00")

    def test_list_transactions_multiple_filters(self):
        """Test applying multiple filters simultaneously."""
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        mock_transactions = [
            Transaction(
                transaction_id=1,
                account_id=5,
                category_id=10,
                payee_id=20,
                transaction_type="expense",
                status="cleared",
                amount=Decimal("100.00"),
                transaction_date=date(2024, 1, 15)
            ),
        ]

        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_transactions

        transactions, total = list_transactions(
            mock_db,
            account_id=5,
            category_id=10,
            payee_id=20,
            transaction_type=TransactionType.EXPENSE,
            status=TransactionStatus.CLEARED,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )

        assert total == 1
        assert len(transactions) == 1
        assert transactions[0].account_id == 5
        assert transactions[0].category_id == 10

    def test_list_transactions_empty_result(self):
        """Test when no transactions match the filters."""
        mock_db = Mock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query

        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []

        transactions, total = list_transactions(
            mock_db,
            account_id=999  # Non-existent account
        )

        assert total == 0
        assert len(transactions) == 0
