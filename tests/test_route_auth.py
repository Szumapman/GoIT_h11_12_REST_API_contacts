from unittest.mock import MagicMock

from src.database.models import User


def test_signup_success(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert data["detail"] == "User successfully created"


def test_signup_failure_user_already_exists(client, user):
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
