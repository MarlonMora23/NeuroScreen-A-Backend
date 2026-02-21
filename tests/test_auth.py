import pytest


class TestLogin:

    def test_login_success(self, client, admin_user):
        response = client.post("/api/auth/login", json={
            "email": "admin@neuroscreen.com",
            "password": "Admin123"
        })
        data = response.get_json()
        assert response.status_code == 200
        assert "access_token" in data
        assert data["user"]["email"] == "admin@neuroscreen.com"
        assert data["user"]["role"] == "admin"
        assert "expires_in" in data

    def test_login_wrong_password(self, client, admin_user):
        response = client.post("/api/auth/login", json={
            "email": "admin@neuroscreen.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 401
        assert "error" in response.get_json()

    def test_login_nonexistent_email(self, client):
        response = client.post("/api/auth/login", json={
            "email": "noexiste@neuroscreen.com",
            "password": "Admin123"
        })
        # Mismo mensaje que contraseña incorrecta — no revelar qué usuarios existen
        assert response.status_code == 401
        assert response.get_json()["error"] == "Invalid credentials"

    def test_login_missing_fields(self, client):
        response = client.post("/api/auth/login", json={"email": "admin@neuroscreen.com"})
        assert response.status_code == 401

    def test_login_empty_body(self, client):
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 401

    def test_login_invalidates_previous_session(self, client, admin_user):
        """Un segundo login invalida el token anterior."""
        r1 = client.post("/api/auth/login", json={
            "email": "admin@neuroscreen.com",
            "password": "Admin123"
        })
        token1 = r1.get_json()["access_token"]

        # Segundo login
        client.post("/api/auth/login", json={
            "email": "admin@neuroscreen.com",
            "password": "Admin123"
        })

        # Token anterior debe ser rechazado
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert response.status_code == 401


class TestLogout:

    def test_logout_success(self, client, admin_headers):
        response = client.post("/api/auth/logout", headers=admin_headers)
        assert response.status_code == 200

    def test_token_invalid_after_logout(self, client, admin_user):
        r = client.post("/api/auth/login", json={
            "email": "admin@neuroscreen.com",
            "password": "Admin123"
        })
        token = r.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        client.post("/api/auth/logout", headers=headers)

        # El token ya no debería funcionar
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

    def test_logout_requires_auth(self, client):
        response = client.post("/api/auth/logout")
        assert response.status_code == 401


class TestMe:

    def test_me_returns_current_user(self, client, admin_headers, admin_user):
        response = client.get("/api/auth/me", headers=admin_headers)
        data = response.get_json()
        assert response.status_code == 200
        assert data["email"] == "admin@neuroscreen.com"
        assert data["role"] == "admin"

    def test_me_requires_auth(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_with_invalid_token(self, client):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer token_inventado"}
        )
        assert response.status_code == 401
