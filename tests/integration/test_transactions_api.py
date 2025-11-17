"""
Integration tests for transaction API endpoints.
Tests transaction creation and retrieval through HTTP requests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date


def test_create_transaction_success(client: TestClient, db_session: Session):
    """Test successful transaction creation."""
    # First create an account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Test Account for Transaction",
        "currency_code": "USD",
        "opening_balance": "1000.00"
    })
    account_id = account_response.json()["account_id"]

    # Create a transaction
    response = client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "50.00",
        "currency_code": "USD",
        "base_amount": "50.00",
        "transaction_date": "2025-01-15",
        "description": "Test expense"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "50.00"
    assert data["transaction_type"] == "expense"
    assert data["description"] == "Test expense"
    assert "transaction_id" in data
    assert data["status"] == "cleared"  # Default value


def test_create_transaction_income(client: TestClient, db_session: Session):
    """Test creating an income transaction."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Income Test Account",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create income transaction
    response = client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount": "2000.00",
        "currency_code": "USD",
        "base_amount": "2000.00",
        "transaction_date": "2025-01-15"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["transaction_type"] == "income"


def test_create_transaction_with_optional_fields(client: TestClient, db_session: Session):
    """Test transaction creation with optional fields."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Optional Fields Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create transaction with optional fields
    response = client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "75.50",
        "currency_code": "USD",
        "base_amount": "75.50",
        "transaction_date": "2025-01-15",
        "status": "pending",
        "description": "Grocery shopping",
        "reference_number": "CHK-123",
        "location": "Whole Foods",
        "notes": "Weekly groceries"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["description"] == "Grocery shopping"
    assert data["reference_number"] == "CHK-123"
    assert data["location"] == "Whole Foods"
    assert data["notes"] == "Weekly groceries"


def test_create_transaction_invalid_account(client: TestClient, db_session: Session):
    """Test transaction creation with invalid account_id."""
    response = client.post("/transactions", json={
        "account_id": 99999,
        "transaction_type": "expense",
        "amount": "50.00",
        "currency_code": "USD",
        "base_amount": "50.00",
        "transaction_date": "2025-01-15"
    })
    assert response.status_code == 422
    assert "VALIDATION_ERROR" in response.text


def test_create_transaction_invalid_amount(client: TestClient, db_session: Session):
    """Test transaction creation with negative amount."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Invalid Amount Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Try to create transaction with negative amount
    response = client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "-50.00",
        "currency_code": "USD",
        "base_amount": "50.00",
        "transaction_date": "2025-01-15"
    })
    assert response.status_code == 422  # Validation error


def test_get_transaction_success(client: TestClient, db_session: Session):
    """Test retrieving an existing transaction."""
    # Create account and transaction
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Get Test Account",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    create_response = client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-15",
        "description": "Get test transaction"
    })
    transaction_id = create_response.json()["transaction_id"]

    # Get the transaction
    response = client.get(f"/transactions/{transaction_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == transaction_id
    assert data["description"] == "Get test transaction"
    assert data["amount"] == "100.00"


def test_get_transaction_not_found(client: TestClient, db_session: Session):
    """Test retrieving a non-existent transaction."""
    response = client.get("/transactions/99999")
    assert response.status_code == 404
    assert "NOT_FOUND" in response.text


def test_transaction_balance_update(client: TestClient, db_session: Session):
    """
    Test that account balance is automatically updated by database triggers.
    This is a critical integration test for the database trigger functionality.
    """
    # Create account with opening balance
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Balance Update Test",
        "currency_code": "USD",
        "opening_balance": "1000.00"
    })
    account_id = account_response.json()["account_id"]
    initial_balance = float(account_response.json()["current_balance"])

    # Create an expense transaction
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "200.00",
        "currency_code": "USD",
        "base_amount": "200.00",
        "transaction_date": "2025-01-15"
    })

    # Check that account balance decreased
    account_check = client.get(f"/accounts/{account_id}")
    new_balance = float(account_check.json()["current_balance"])
    assert new_balance == initial_balance - 200.00

    # Create an income transaction
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount": "500.00",
        "currency_code": "USD",
        "base_amount": "500.00",
        "transaction_date": "2025-01-16"
    })

    # Check that account balance increased
    account_check = client.get(f"/accounts/{account_id}")
    final_balance = float(account_check.json()["current_balance"])
    assert final_balance == new_balance + 500.00


def test_transaction_date_format(client: TestClient, db_session: Session):
    """Test that transaction date accepts ISO 8601 format."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Date Format Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create transaction with ISO date
    response = client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "25.00",
        "currency_code": "USD",
        "base_amount": "25.00",
        "transaction_date": "2025-01-15"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["transaction_date"] == "2025-01-15"


# ===== Phase 7 Tests: List and Filter Transactions =====

def test_list_transactions_empty(client: TestClient, db_session: Session):
    """Test listing transactions when no transactions exist."""
    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert data["data"] == []
    assert data["pagination"]["total"] == 0
    assert data["pagination"]["limit"] == 50
    assert data["pagination"]["offset"] == 0


def test_list_transactions_basic(client: TestClient, db_session: Session):
    """Test basic transaction listing."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "List Test Account",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create multiple transactions
    for i in range(3):
        client.post("/transactions", json={
            "account_id": account_id,
            "transaction_type": "expense",
            "amount": f"{(i+1) * 10}.00",
            "currency_code": "USD",
            "base_amount": f"{(i+1) * 10}.00",
            "transaction_date": f"2025-01-{15+i:02d}"
        })

    # List transactions
    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["pagination"]["total"] == 3


def test_list_transactions_filter_by_account(client: TestClient, db_session: Session):
    """Test filtering transactions by account_id."""
    # Create two accounts
    account1_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Account 1",
        "currency_code": "USD"
    })
    account1_id = account1_response.json()["account_id"]

    account2_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Account 2",
        "currency_code": "USD"
    })
    account2_id = account2_response.json()["account_id"]

    # Create transactions for both accounts
    client.post("/transactions", json={
        "account_id": account1_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-15"
    })
    client.post("/transactions", json={
        "account_id": account2_id,
        "transaction_type": "expense",
        "amount": "200.00",
        "currency_code": "USD",
        "base_amount": "200.00",
        "transaction_date": "2025-01-16"
    })

    # Filter by account1
    response = client.get(f"/transactions?account_id={account1_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["account_id"] == account1_id
    assert data["pagination"]["total"] == 1


def test_list_transactions_filter_by_type(client: TestClient, db_session: Session):
    """Test filtering transactions by transaction_type."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Type Filter Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create income and expense transactions
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-15"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount": "500.00",
        "currency_code": "USD",
        "base_amount": "500.00",
        "transaction_date": "2025-01-16"
    })

    # Filter by income
    response = client.get("/transactions?transaction_type=income")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["transaction_type"] == "income"


def test_list_transactions_filter_by_status(client: TestClient, db_session: Session):
    """Test filtering transactions by status."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Status Filter Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create transactions with different statuses
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-15",
        "status": "pending"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "200.00",
        "currency_code": "USD",
        "base_amount": "200.00",
        "transaction_date": "2025-01-16",
        "status": "cleared"
    })

    # Filter by pending status
    response = client.get("/transactions?status=pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["status"] == "pending"


def test_list_transactions_filter_by_date_range(client: TestClient, db_session: Session):
    """Test filtering transactions by date range."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Date Range Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create transactions on different dates
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-10"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "200.00",
        "currency_code": "USD",
        "base_amount": "200.00",
        "transaction_date": "2025-01-15"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "300.00",
        "currency_code": "USD",
        "base_amount": "300.00",
        "transaction_date": "2025-01-20"
    })

    # Filter by date range (Jan 12-18)
    response = client.get("/transactions?start_date=2025-01-12&end_date=2025-01-18")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["transaction_date"] == "2025-01-15"


def test_list_transactions_pagination(client: TestClient, db_session: Session):
    """Test transaction pagination."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Pagination Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create 10 transactions
    for i in range(10):
        client.post("/transactions", json={
            "account_id": account_id,
            "transaction_type": "expense",
            "amount": f"{(i+1) * 10}.00",
            "currency_code": "USD",
            "base_amount": f"{(i+1) * 10}.00",
            "transaction_date": f"2025-01-{10+i:02d}"
        })

    # Get first page (limit 5)
    response = client.get("/transactions?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["pagination"]["limit"] == 5
    assert data["pagination"]["offset"] == 0
    assert data["pagination"]["total"] == 10

    # Get second page
    response = client.get("/transactions?limit=5&offset=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["pagination"]["offset"] == 5


def test_list_transactions_sorting_by_date_desc(client: TestClient, db_session: Session):
    """Test sorting transactions by date in descending order (default)."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Sort Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create transactions
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-10"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "200.00",
        "currency_code": "USD",
        "base_amount": "200.00",
        "transaction_date": "2025-01-20"
    })

    # Default sort (date desc)
    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.json()
    assert data["data"][0]["transaction_date"] == "2025-01-20"
    assert data["data"][1]["transaction_date"] == "2025-01-10"


def test_list_transactions_sorting_by_date_asc(client: TestClient, db_session: Session):
    """Test sorting transactions by date in ascending order."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Sort Asc Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create transactions
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-10"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "200.00",
        "currency_code": "USD",
        "base_amount": "200.00",
        "transaction_date": "2025-01-20"
    })

    # Sort by date asc
    response = client.get("/transactions?sort=transaction_date&order=asc")
    assert response.status_code == 200
    data = response.json()
    assert data["data"][0]["transaction_date"] == "2025-01-10"
    assert data["data"][1]["transaction_date"] == "2025-01-20"


def test_list_transactions_sorting_by_amount(client: TestClient, db_session: Session):
    """Test sorting transactions by amount."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Amount Sort Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create transactions with different amounts
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "300.00",
        "currency_code": "USD",
        "base_amount": "300.00",
        "transaction_date": "2025-01-15"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-16"
    })

    # Sort by amount asc
    response = client.get("/transactions?sort=amount&order=asc")
    assert response.status_code == 200
    data = response.json()
    assert data["data"][0]["amount"] == "100.00"
    assert data["data"][1]["amount"] == "300.00"


def test_list_transactions_invalid_sort_field(client: TestClient, db_session: Session):
    """Test that invalid sort field returns validation error."""
    response = client.get("/transactions?sort=invalid_field")
    assert response.status_code == 400
    assert "VALIDATION_ERROR" in response.text


def test_list_transactions_pagination_limit_validation(client: TestClient, db_session: Session):
    """Test that limit is capped at 100."""
    response = client.get("/transactions?limit=200")
    assert response.status_code == 422  # Validation error


def test_list_transactions_multiple_filters(client: TestClient, db_session: Session):
    """Test applying multiple filters simultaneously."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Multi Filter Test",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create various transactions
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-15",
        "status": "pending"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "200.00",
        "currency_code": "USD",
        "base_amount": "200.00",
        "transaction_date": "2025-01-20",
        "status": "cleared"
    })
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount": "500.00",
        "currency_code": "USD",
        "base_amount": "500.00",
        "transaction_date": "2025-01-18",
        "status": "cleared"
    })

    # Filter: expense + cleared + date range
    response = client.get(
        f"/transactions?account_id={account_id}&transaction_type=expense&status=cleared&start_date=2025-01-12&end_date=2025-01-25"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["amount"] == "200.00"
    assert data["data"][0]["status"] == "cleared"
