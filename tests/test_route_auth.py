import pytest
from unittest.mock import MagicMock, patch
from fastapi.security import HTTPAuthorizationCredentials

from src.services.auth import auth_service
from src.database.models import User


def test_signup_success(client, user, monkeypatch):
    with patch.object(auth_service, "redis_base") as mock_redis:
        mock_redis.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
        response = client.post("/api/auth/signup", json=user)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["user"]["email"] == user.get("email")
        assert data["detail"] == "User successfully created"


def test_signup_failure_user_already_exists(client, user):
    with patch.object(auth_service, "redis_base") as mock_redis:
        mock_redis.get.return_value = None
        response = client.post("/api/auth/signup", json=user)
        assert response.status_code == 409, response.text
        data = response.json()
        assert data["detail"] == f"User with email: {user.get('email')} already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_success(client, session, user):
    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_failure_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": "wrong_password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect email or password"


def test_login_failure_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": "wrong_email", "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect email or password"
