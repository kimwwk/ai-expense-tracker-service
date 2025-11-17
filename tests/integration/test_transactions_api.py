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
