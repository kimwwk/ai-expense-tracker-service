"""
Integration tests for account API endpoints.
Tests the full account CRUD lifecycle through HTTP requests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_create_account_success(client: TestClient, db_session: Session):
    """Test successful account creation."""
    response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Test Checking",
        "currency_code": "USD",
        "opening_balance": "1000.00"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["account_name"] == "Test Checking"
    assert data["opening_balance"] == "1000.00"
    assert data["current_balance"] == "1000.00"
    assert "account_id" in data


def test_create_account_invalid_foreign_key(client: TestClient, db_session: Session):
    """Test account creation with invalid account_type_id."""
    response = client.post("/accounts", json={
        "account_type_id": 9999,
        "account_name": "Invalid Account",
        "currency_code": "USD"
    })
    assert response.status_code == 422
    assert "VALIDATION_ERROR" in response.text


def test_get_account_success(client: TestClient, db_session: Session):
    """Test retrieving an existing account."""
    # Create account first
    create_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Get Test Account",
        "currency_code": "USD"
    })
    account_id = create_response.json()["account_id"]

    # Get the account
    response = client.get(f"/accounts/{account_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == account_id
    assert data["account_name"] == "Get Test Account"


def test_get_account_not_found(client: TestClient, db_session: Session):
    """Test retrieving a non-existent account."""
    response = client.get("/accounts/99999")
    assert response.status_code == 404
    assert "NOT_FOUND" in response.text


def test_list_accounts(client: TestClient, db_session: Session):
    """Test listing accounts with pagination."""
    # Create multiple accounts
    for i in range(3):
        client.post("/accounts", json={
            "account_type_id": 1,
            "account_name": f"List Test Account {i}",
            "currency_code": "USD"
        })

    # List all accounts
    response = client.get("/accounts")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) >= 3
    assert data["pagination"]["total"] >= 3


def test_list_accounts_with_filters(client: TestClient, db_session: Session):
    """Test listing accounts with filters."""
    # Create accounts with different attributes
    client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "USD Account",
        "currency_code": "USD"
    })
    client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "GBP Account",
        "currency_code": "GBP"
    })

    # Filter by currency
    response = client.get("/accounts?currency_code=USD")
    assert response.status_code == 200
    data = response.json()
    for account in data["data"]:
        assert account["currency_code"] == "USD"


def test_update_account_patch(client: TestClient, db_session: Session):
    """Test partial account update using PATCH."""
    # Create account
    create_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Original Name",
        "currency_code": "USD"
    })
    account_id = create_response.json()["account_id"]

    # Partially update
    response = client.patch(f"/accounts/{account_id}", json={
        "account_name": "Updated Name"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["account_name"] == "Updated Name"
    assert data["currency_code"] == "USD"  # Unchanged


def test_update_account_put(client: TestClient, db_session: Session):
    """Test full account update using PUT."""
    # Create account
    create_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Original Name",
        "currency_code": "USD",
        "notes": "Original notes"
    })
    account_id = create_response.json()["account_id"]

    # Full update
    response = client.put(f"/accounts/{account_id}", json={
        "account_name": "Fully Updated Name",
        "account_type_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["account_name"] == "Fully Updated Name"


def test_update_account_not_found(client: TestClient, db_session: Session):
    """Test updating a non-existent account."""
    response = client.patch("/accounts/99999", json={
        "account_name": "Updated"
    })
    assert response.status_code == 404


def test_delete_account_success(client: TestClient, db_session: Session):
    """Test successful account deletion."""
    # Create account
    create_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "To Delete",
        "currency_code": "USD"
    })
    account_id = create_response.json()["account_id"]

    # Delete account
    response = client.delete(f"/accounts/{account_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/accounts/{account_id}")
    assert get_response.status_code == 404


def test_delete_account_not_found(client: TestClient, db_session: Session):
    """Test deleting a non-existent account."""
    response = client.delete("/accounts/99999")
    assert response.status_code == 404


def test_pagination(client: TestClient, db_session: Session):
    """Test pagination parameters."""
    # Create multiple accounts
    for i in range(5):
        client.post("/accounts", json={
            "account_type_id": 1,
            "account_name": f"Pagination Test {i}",
            "currency_code": "USD"
        })

    # Test with limit
    response = client.get("/accounts?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) <= 2
    assert data["pagination"]["limit"] == 2

    # Test with offset
    response = client.get("/accounts?limit=2&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["offset"] == 2
