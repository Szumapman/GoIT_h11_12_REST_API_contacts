import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_limiter import FastAPILimiter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, startup_event
from src.database.models import Base
from src.database.dependencies import get_user_repository, get_contact_repository
from src.repository.users import PostgresUserRepository
from src.repository.contacts import PostgresContactRepository

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def client(session):

    def override_get_user_repository():
        try:
            yield PostgresUserRepository(session)
        finally:
            session.close()

    app.dependency_overrides[get_user_repository] = override_get_user_repository

    def override_get_contact_repository():
        try:
            yield PostgresContactRepository(session)
        finally:
            session.close()

    app.dependency_overrides[get_contact_repository] = override_get_contact_repository

    with TestClient(app) as test_client:
        yield test_client
    # yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {
        "username": "testuser",
        "email": "example_mail@example.com",
        "password": "Password1!",
    }
