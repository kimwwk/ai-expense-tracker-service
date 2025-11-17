"""
Integration tests for category API endpoints.
Tests category creation, retrieval, update, and deletion through HTTP requests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_create_category_success(client: TestClient, db_session: Session):
    """Test successful category creation."""
    response = client.post("/categories", json={
        "category_name": "Groceries",
        "category_type": "expense",
        "category_group": "Food",
        "color_code": "#FF5733"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["category_name"] == "Groceries"
    assert data["category_type"] == "expense"
    assert data["category_group"] == "Food"
    assert data["color_code"] == "#FF5733"
    assert "category_id" in data
    assert data["is_active"] is True


def test_create_category_minimal(client: TestClient, db_session: Session):
    """Test creating category with only required fields."""
    response = client.post("/categories", json={
        "category_name": "Salary",
        "category_type": "income"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["category_name"] == "Salary"
    assert data["category_type"] == "income"
    assert data["is_active"] is True


def test_get_category_success(client: TestClient, db_session: Session):
    """Test retrieving an existing category."""
    # Create category
    create_response = client.post("/categories", json={
        "category_name": "Utilities",
        "category_type": "expense"
    })
    category_id = create_response.json()["category_id"]

    # Get the category
    response = client.get(f"/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == category_id
    assert data["category_name"] == "Utilities"


def test_get_category_not_found(client: TestClient, db_session: Session):
    """Test retrieving a non-existent category."""
    response = client.get("/categories/99999")
    assert response.status_code == 404
    assert "NOT_FOUND" in response.text


def test_list_categories_empty(client: TestClient, db_session: Session):
    """Test listing categories when no categories exist."""
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)


def test_list_categories_basic(client: TestClient, db_session: Session):
    """Test basic category listing."""
    # Create multiple categories
    client.post("/categories", json={
        "category_name": "Transport",
        "category_type": "expense"
    })
    client.post("/categories", json={
        "category_name": "Investment",
        "category_type": "income"
    })

    # List categories
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 2
    assert data["pagination"]["total"] >= 2


def test_list_categories_filter_by_type(client: TestClient, db_session: Session):
    """Test filtering categories by type."""
    # Create categories
    client.post("/categories", json={
        "category_name": "Dining Out",
        "category_type": "expense"
    })
    client.post("/categories", json={
        "category_name": "Bonus",
        "category_type": "income"
    })

    # Filter by expense type
    response = client.get("/categories?category_type=expense")
    assert response.status_code == 200
    data = response.json()
    for category in data["data"]:
        assert category["category_type"] == "expense"


def test_list_categories_filter_by_group(client: TestClient, db_session: Session):
    """Test filtering categories by category_group."""
    # Create categories with groups
    client.post("/categories", json={
        "category_name": "Groceries",
        "category_type": "expense",
        "category_group": "Food"
    })
    client.post("/categories", json={
        "category_name": "Restaurants",
        "category_type": "expense",
        "category_group": "Food"
    })
    client.post("/categories", json={
        "category_name": "Gas",
        "category_type": "expense",
        "category_group": "Transportation"
    })

    # Filter by Food group
    response = client.get("/categories?category_group=Food")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 2
    for category in data["data"]:
        assert category["category_group"] == "Food"


def test_list_categories_filter_by_active_status(client: TestClient, db_session: Session):
    """Test filtering categories by active status."""
    # Create active and inactive categories
    client.post("/categories", json={
        "category_name": "Active Category",
        "category_type": "expense",
        "is_active": True
    })
    inactive_response = client.post("/categories", json={
        "category_name": "Inactive Category",
        "category_type": "expense",
        "is_active": False
    })

    # Filter by active=true
    response = client.get("/categories?is_active=true")
    assert response.status_code == 200
    data = response.json()
    for category in data["data"]:
        assert category["is_active"] is True


def test_list_categories_pagination(client: TestClient, db_session: Session):
    """Test category pagination."""
    # Create multiple categories
    for i in range(5):
        client.post("/categories", json={
            "category_name": f"Category {i}",
            "category_type": "expense"
        })

    # Get first page
    response = client.get("/categories?limit=3&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["limit"] == 3
    assert data["pagination"]["offset"] == 0


def test_update_category_put(client: TestClient, db_session: Session):
    """Test full category update (PUT)."""
    # Create category
    create_response = client.post("/categories", json={
        "category_name": "Original Name",
        "category_type": "expense"
    })
    category_id = create_response.json()["category_id"]

    # Update category
    response = client.put(f"/categories/{category_id}", json={
        "category_name": "Updated Name",
        "category_type": "expense",
        "category_group": "New Group"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["category_name"] == "Updated Name"
    assert data["category_group"] == "New Group"


def test_update_category_patch(client: TestClient, db_session: Session):
    """Test partial category update (PATCH)."""
    # Create category
    create_response = client.post("/categories", json={
        "category_name": "Original Name",
        "category_type": "expense",
        "category_group": "Original Group"
    })
    category_id = create_response.json()["category_id"]

    # Partially update category (only name)
    response = client.patch(f"/categories/{category_id}", json={
        "category_name": "Patched Name"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["category_name"] == "Patched Name"
    assert data["category_group"] == "Original Group"  # Should remain unchanged


def test_update_category_not_found(client: TestClient, db_session: Session):
    """Test updating a non-existent category."""
    response = client.patch("/categories/99999", json={
        "category_name": "New Name"
    })
    assert response.status_code == 404
    assert "NOT_FOUND" in response.text


def test_delete_category_success(client: TestClient, db_session: Session):
    """Test successful category deletion."""
    # Create category
    create_response = client.post("/categories", json={
        "category_name": "To Delete",
        "category_type": "expense"
    })
    category_id = create_response.json()["category_id"]

    # Delete category
    response = client.delete(f"/categories/{category_id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = client.get(f"/categories/{category_id}")
    assert get_response.status_code == 404


def test_delete_category_not_found(client: TestClient, db_session: Session):
    """Test deleting a non-existent category."""
    response = client.delete("/categories/99999")
    assert response.status_code == 404


def test_delete_category_with_transactions(client: TestClient, db_session: Session):
    """Test that deletion fails when category is referenced by transactions."""
    # Create account
    account_response = client.post("/accounts", json={
        "account_type_id": 1,
        "account_name": "Test Account",
        "currency_code": "USD"
    })
    account_id = account_response.json()["account_id"]

    # Create category
    category_response = client.post("/categories", json={
        "category_name": "Referenced Category",
        "category_type": "expense"
    })
    category_id = category_response.json()["category_id"]

    # Create transaction with this category
    client.post("/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": "100.00",
        "currency_code": "USD",
        "base_amount": "100.00",
        "transaction_date": "2025-01-15",
        "category_id": category_id
    })

    # Try to delete category - should fail
    response = client.delete(f"/categories/{category_id}")
    assert response.status_code == 409
    assert "CONFLICT" in response.text


def test_create_category_invalid_color(client: TestClient, db_session: Session):
    """Test creating category with invalid hex color code."""
    response = client.post("/categories", json={
        "category_name": "Invalid Color",
        "category_type": "expense",
        "color_code": "INVALID"
    })
    assert response.status_code == 422  # Validation error


def test_category_validation_empty_name(client: TestClient, db_session: Session):
    """Test that empty category name is rejected."""
    response = client.post("/categories", json={
        "category_name": "",
        "category_type": "expense"
    })
    assert response.status_code == 422
