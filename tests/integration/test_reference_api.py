"""
Integration tests for reference data API endpoints.
Tests read-only access to account types and currencies.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_account_types(client: TestClient, db_session: Session):
    """Test retrieving all account types."""
    response = client.get("/reference/account-types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have at least checking, savings, credit_card from seed data
    assert len(data) >= 3
    # Verify structure
    if len(data) > 0:
        account_type = data[0]
        assert "account_type_id" in account_type
        assert "type_name" in account_type
        assert "is_asset" in account_type


def test_get_currencies(client: TestClient, db_session: Session):
    """Test retrieving all currencies."""
    response = client.get("/reference/currencies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have at least USD, GBP, CAD from seed data
    assert len(data) >= 3
    # Verify structure
    if len(data) > 0:
        currency = data[0]
        assert "currency_code" in currency
        assert "currency_name" in currency
        assert "currency_symbol" in currency
        assert "decimal_places" in currency
        assert "is_active" in currency


def test_get_currencies_active_only(client: TestClient, db_session: Session):
    """Test retrieving only active currencies."""
    response = client.get("/reference/currencies?active_only=true")
    assert response.status_code == 200
    data = response.json()
    # All returned currencies should be active
    for currency in data:
        assert currency["is_active"] is True


def test_get_currencies_all(client: TestClient, db_session: Session):
    """Test retrieving all currencies including inactive."""
    response = client.get("/reference/currencies?active_only=false")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
