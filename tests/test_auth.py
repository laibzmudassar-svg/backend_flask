import uuid
from models.user_model import User


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


# ---------------- Integration Tests (real HTTP + DB) ----------------

class TestAuthIntegration:

    def test_register_success(self, client):
        email = unique_email()
        response = client.post("/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": "TestPass123!"
        })
        assert response.status_code == 201
        assert response.get_json()["email"] == email

    def test_register_duplicate_email_fails(self, client):
        email = unique_email()
        client.post("/auth/register", json={
            "name": "Test User", "email": email, "password": "TestPass123!"
        })
        response = client.post("/auth/register", json={
            "name": "Test User 2", "email": email, "password": "AnotherPass123!"
        })
        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_login_success(self, client):
        email = unique_email()
        password = "TestPass123!"
        client.post("/auth/register", json={
            "name": "Login Test", "email": email, "password": password
        })
        response = client.post("/auth/login", json={
            "email": email, "password": password
        })
        assert response.status_code == 200
        assert "token" in response.get_json()

    def test_login_wrong_password_fails(self, client):
        email = unique_email()
        client.post("/auth/register", json={
            "name": "Wrong Pass Test", "email": email, "password": "CorrectPass123!"
        })
        response = client.post("/auth/login", json={
            "email": email, "password": "WrongPassword!"
        })
        assert response.status_code == 401


# ---------------- Unit Test (isolated business logic check) ----------------

class TestAuthUnit:

    def test_password_is_hashed_not_plaintext(self, client, app):
        email = unique_email()
        password = "PlainTextPass123!"
        client.post("/auth/register", json={
            "name": "Hash Test", "email": email, "password": password
        })
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            assert user.password_hash != password
            assert user.password_hash.startswith("$2b$")
            