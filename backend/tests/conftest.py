"""Test configuration.

Tests run against an isolated in-memory SQLite database rather than
PostgreSQL, so they need no external services and never touch development
or production data (see BACKEND_ASSUMPTIONS.md for the trade-off). The
schema is created directly from the SQLAlchemy models — production schema
correctness is instead verified by actually running the Alembic migration
against PostgreSQL (see README "Running tests").
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.service import Service
from app.seed_data import SERVICES

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    for service in SERVICES:
        session.add(Service(**service, is_active=True))
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def valid_booking_payload() -> dict:
    return {
        "full_name": "Ravi Kumar",
        "phone": "8824276600",
        "email": "ravi@example.com",
        "city": "Pali",
        "service": "AC & Cooling",
        "message": "AC is not cooling and making a rattling noise.",
    }
