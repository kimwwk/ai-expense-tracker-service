"""
Integration tests for payee API endpoints.
Tests payee creation, retrieval, update, and deletion through HTTP requests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_create_payee_success(client: TestClient, db_session: Session):
    """Test successful payee creation."""
    response = client.post("/payees", json={
        "payee_name": "Amazon",
        "notes": "Online shopping"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["payee_name"] == "Amazon"
    assert data["notes"] == "Online shopping"
    assert "payee_id" in data
    assert data["is_active"] is True


def test_create_payee_minimal(client: TestClient, db_session: Session):
    """Test creating payee with only required fields."""
    response = client.post("/payees", json={
        "payee_name": "Starbucks"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["payee_name"] == "Starbucks"
    assert data["is_active"] is True


def test_create_payee_with_default_category(client: TestClient, db_session: Session):
    """Test creating payee with default category."""
    # First create a category
    category_response = client.post("/categories", json={
        "category_name": "Groceries",
        "category_type": "expense"
    })
    category_id = category_response.json()["category_id"]

    # Create payee with default category
    response = client.post("/payees", json={
        "payee_name": "Whole Foods",
        "default_category_id": category_id
    })
    assert response.status_code == 201
    data = response.json()
    assert data["payee_name"] == "Whole Foods"
    assert data["default_category_id"] == category_id


def test_create_payee_invalid_category(client: TestClient, db_session: Session):
    """Test creating payee with non-existent category."""
    response = client.post("/payees", json={
        "payee_name": "Test Payee",
        "default_category_id": 99999
    })
    assert response.status_code == 422
    assert "VALIDATION_ERROR" in response.text


def test_get_payee_success(client: TestClient, db_session: Session):
    """Test retrieving an existing payee."""
    # Create payee
    create_response = client.post("/payees", json={
        "payee_name": "Target"
    })
    payee_id = create_response.json()["payee_id"]

    # Get the payee
    response = client.get(f"/payees/{payee_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["payee_id"] == payee_id
    assert data["payee_name"] == "Target"


def test_get_payee_not_found(client: TestClient, db_session: Session):
    """Test retrieving a non-existent payee."""
    response = client.get("/payees/99999")
    assert response.status_code == 404
    assert "NOT_FOUND" in response.text


def test_list_payees_empty(client: TestClient, db_session: Session):
    """Test listing payees when no payees exist."""
    response = client.get("/payees")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)


def test_list_payees_basic(client: TestClient, db_session: Session):
    """Test basic payee listing."""
    # Create multiple payees
    client.post("/payees", json={
        "payee_name": "Walmart"
    })
    client.post("/payees", json={
        "payee_name": "Costco"
    })

    # List payees
    response = client.get("/payees")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 2
    assert data["pagination"]["total"] >= 2


def test_list_payees_filter_by_active_status(client: TestClient, db_session: Session):
    """Test filtering payees by active status."""
    # Create active and inactive payees
    client.post("/payees", json={
        "payee_name": "Active Payee",
        "is_active": True
    })
    client.post("/payees", json={
        "payee_name": "Inactive Payee",
        "is_active": False
    })

    # Filter by active=true
    response = client.get("/payees?is_active=true")
    assert response.status_code == 200
    data = response.json()
    for payee in data["data"]:
        assert payee["is_active"] is True

    # Filter by active=false
    response = client.get("/payees?is_active=false")
    assert response.status_code == 200
    data = response.json()
    for payee in data["data"]:
        assert payee["is_active"] is False


def test_list_payees_pagination(client: TestClient, db_session: Session):
    """Test payee pagination."""
    # Create multiple payees
    for i in range(5):
        client.post("/payees", json={
            "payee_name": f"Payee {i}"
        })

    # Get first page
    response = client.get("/payees?limit=3&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["limit"] == 3
    assert data["pagination"]["offset"] == 0


def test_update_payee_put(client: TestClient, db_session: Session):
    """Test full payee update (PUT)."""
    # Create payee
    create_response = client.post("/payees", json={
        "payee_name": "Original Name",
        "notes": "Original notes"
    })
    payee_id = create_response.json()["payee_id"]

    # Update payee
    response = client.put(f"/payees/{payee_id}", json={
        "payee_name": "Updated Name",
        "notes": "Updated notes"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["payee_name"] == "Updated Name"
    assert data["notes"] == "Updated notes"


def test_update_payee_patch(client: TestClient, db_session: Session):
    """Test partial payee update (PATCH)."""
    # Create payee
    create_response = client.post("/payees", json={
        "payee_name": "Original Name",
        "notes": "Original notes"
    })
    payee_id = create_response.json()["payee_id"]

    # Partially update payee (only name)
    response = client.patch(f"/payees/{payee_id}", json={
        "payee_name": "Patched Name"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["payee_name"] == "Patched Name"
    assert data["notes"] == "Original notes"  # Should remain unchanged


def test_update_payee_not_found(client: TestClient, db_session: Session):
    """Test updating a non-existent payee."""
    response = client.patch("/payees/99999", json={
        "payee_name": "New Name"
    })
    assert response.status_code == 404
    assert "NOT_FOUND" in response.text


def test_update_payee_invalid_category(client: TestClient, db_session: Session):
    """Test updating payee with invalid category ID."""
    # Create payee
    create_response = client.post("/payees", json={
        "payee_name": "Test Payee"
    })
    payee_id = create_response.json()["payee_id"]

    # Try to update with non-existent category
    response = client.patch(f"/payees/{payee_id}", json={
        "default_category_id": 99999
    })
    assert response.status_code == 422
    assert "VALIDATION_ERROR" in response.text


def test_delete_payee_success(client: TestClient, db_session: Session):
    """Test successful payee deletion."""
    # Create payee
    create_response = client.post("/payees", json={
        "payee_name": "To Delete"
    })
    payee_id = create_response.json()["payee_id"]

    # Delete payee
    response = client.delete(f"/payees/{payee_id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = client.get(f"/payees/{payee_id}")
    assert get_response.status_code == 404


def test_delete_payee_not_found(client: TestClient, db_session: Session):
    """Test deleting a non-existent payee."""
    response = client.delete("/payees/99999")
    assert response.status_code == 404


def test_delete_payee_with_transactions(client: TestClient, db_session: Session):
    """Test that deletion fails when payee is referenced by transactions."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Test Account",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create payee
    payee_response = client.post("/payees", json={
        "payee_name": "Referenced Payee"
    })
    payee_id = payee_response.json()["payee_id"]

    # Create transaction with this payee
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-15",
        "payee_id": payee_id
    })

    # Try to delete payee - should fail
    response = client.delete(f"/payees/{payee_id}")
    assert response.status_code == 409
    assert "CONFLICT" in response.text


def test_payee_validation_empty_name(client: TestClient, db_session: Session):
    """Test that empty payee name is rejected."""
    response = client.post("/payees", json={
        "payee_name": ""
    })
    assert response.status_code == 422


def test_payee_alphabetical_sorting(client: TestClient, db_session: Session):
    """Test that payees are returned in alphabetical order."""
    # Create payees in non-alphabetical order
    client.post("/payees", json={"payee_name": "Zebra Corp"})
    client.post("/payees", json={"payee_name": "Apple Store"})
    client.post("/payees", json={"payee_name": "Microsoft"})

    # List payees
    response = client.get("/payees")
    assert response.status_code == 200
    data = response.json()

    # Extract names and verify they're in alphabetical order
    names = [payee["payee_name"] for payee in data["data"]]
    assert names == sorted(names)


def test_payee_update_change_default_category(client: TestClient, db_session: Session):
    """Test updating payee's default category."""
    # Create categories
    cat1_response = client.post("/categories", json={
        "category_name": "Food",
        "category_type": "expense"
    })
    cat1_id = cat1_response.json()["category_id"]

    cat2_response = client.post("/categories", json={
        "category_name": "Entertainment",
        "category_type": "expense"
    })
    cat2_id = cat2_response.json()["category_id"]

    # Create payee with first category
    payee_response = client.post("/payees", json={
        "payee_name": "Restaurant",
        "default_category_id": cat1_id
    })
    payee_id = payee_response.json()["payee_id"]

    # Update to second category
    update_response = client.patch(f"/payees/{payee_id}", json={
        "default_category_id": cat2_id
    })
    assert update_response.status_code == 200
    assert update_response.json()["default_category_id"] == cat2_id


def test_payee_deactivation(client: TestClient, db_session: Session):
    """Test deactivating a payee."""
    # Create active payee
    create_response = client.post("/payees", json={
        "payee_name": "Active Payee",
        "is_active": True
    })
    payee_id = create_response.json()["payee_id"]

    # Deactivate payee
    response = client.patch(f"/payees/{payee_id}", json={
        "is_active": False
    })
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Verify it still exists but is inactive
    get_response = client.get(f"/payees/{payee_id}")
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False
