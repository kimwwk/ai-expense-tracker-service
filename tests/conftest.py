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

# Test database URL - use a separate test database
TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/expense_tracker_test"


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Provides an isolated database session for each test.
    Creates tables before test, rolls back changes after test.
    """
    # Create test engine
    engine = create_engine(TEST_DATABASE_URL)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


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
