"""
Pytest configuration and shared fixtures.
Provides database session and test client fixtures for all tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.main import app
from src.database import Base, get_db

# Test database URL - use the same database as dev for now
# In production, you should use a separate test database
TEST_DATABASE_URL = "postgresql://expense_user:expense_tracker_password@localhost:5432/expense_tracker_db"


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Provides an isolated database session for each test.
    Uses transactions and rolls back changes after each test to maintain isolation.
    """
    # Create test engine
    engine = create_engine(TEST_DATABASE_URL)

    # Create connection and transaction
    connection = engine.connect()
    transaction = connection.begin()

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Rollback the transaction to undo all changes
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """
    Provides a FastAPI test client with the test database session.
    Overrides the get_db dependency to use the test session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up override
    app.dependency_overrides.clear()
