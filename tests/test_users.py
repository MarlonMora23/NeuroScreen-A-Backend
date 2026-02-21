import pytest


class TestCreateUser:

    def test_admin_can_create_user(self, client, admin_headers):
        response = client.post("/api/users", json={
            "email": "nuevo@neuroscreen.com",
            "password": "Password123",
            "first_name": "Nuevo",
            "last_name": "Usuario"
        }, headers=admin_headers)
        data = response.get_json()
        assert response.status_code == 201
        assert data["email"] == "nuevo@neuroscreen.com"
        assert "password_hash" not in data

    def test_regular_user_cannot_create_user(self, client, user_headers):
        response = client.post("/api/users", json={
            "email": "otro@neuroscreen.com",
            "password": "Password123",
            "first_name": "Otro",
            "last_name": "Usuario"
        }, headers=user_headers)
        assert response.status_code == 403

    def test_create_user_missing_fields(self, client, admin_headers):
        response = client.post("/api/users", json={
            "email": "incompleto@neuroscreen.com"
        }, headers=admin_headers)
        assert response.status_code == 400

    def test_create_user_duplicate_email(self, client, admin_headers, regular_user):
        response = client.post("/api/users", json={
            "email": "doctor@neuroscreen.com",  # ya existe
            "password": "Password123",
            "first_name": "Duplicado",
            "last_name": "Test"
        }, headers=admin_headers)
        assert response.status_code == 400

    def test_create_user_requires_auth(self, client):
        response = client.post("/api/users", json={
            "email": "x@x.com",
            "password": "Pass123",
            "first_name": "X",
            "last_name": "X"
        })
        assert response.status_code == 401


class TestListUsers:

    def test_admin_can_list_users(self, client, admin_headers, regular_user):
        response = client.get("/api/users", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)

    def test_regular_user_cannot_list_users(self, client, user_headers):
        response = client.get("/api/users", headers=user_headers)
        assert response.status_code == 403

    def test_list_does_not_include_deleted_users(self, client, admin_headers, regular_user):
        # Eliminar el usuario
        client.delete(f"/api/users/{regular_user.id}", headers=admin_headers)
        response = client.get("/api/users", headers=admin_headers)
        ids = [u["id"] for u in response.get_json()]
        assert regular_user.id not in ids


class TestGetUser:

    def test_admin_can_get_any_user(self, client, admin_headers, regular_user):
        response = client.get(f"/api/users/{regular_user.id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.get_json()["id"] == regular_user.id

    def test_user_can_get_itself(self, client, user_headers, regular_user):
        response = client.get(f"/api/users/{regular_user.id}", headers=user_headers)
        assert response.status_code == 200

    def test_user_cannot_get_another_user(self, client, user_headers, admin_user):
        response = client.get(f"/api/users/{admin_user.id}", headers=user_headers)
        assert response.status_code == 403

    def test_get_nonexistent_user(self, client, admin_headers):
        response = client.get("/api/users/99999", headers=admin_headers)
        assert response.status_code == 404


class TestUpdateUser:

    def test_user_can_update_itself(self, client, user_headers, regular_user):
        response = client.put(f"/api/users/{regular_user.id}", json={
            "first_name": "NuevoNombre"
        }, headers=user_headers)
        assert response.status_code == 200
        assert response.get_json()["first_name"] == "NuevoNombre"

    def test_user_cannot_update_role(self, client, user_headers, regular_user):
        response = client.put(f"/api/users/{regular_user.id}", json={
            "role": "admin"
        }, headers=user_headers)
        assert response.status_code == 400

    def test_user_cannot_update_another_user(self, client, user_headers, admin_user):
        response = client.put(f"/api/users/{admin_user.id}", json={
            "first_name": "Hack"
        }, headers=user_headers)
        assert response.status_code == 403

    def test_update_email_duplicate(self, client, admin_headers, regular_user, another_user):
        response = client.put(f"/api/users/{regular_user.id}", json={
            "email": "doctor2@neuroscreen.com"  # email de another_user
        }, headers=admin_headers)
        assert response.status_code == 400


class TestDeleteUser:

    def test_admin_can_delete_user(self, client, admin_headers, regular_user):
        response = client.delete(f"/api/users/{regular_user.id}", headers=admin_headers)
        assert response.status_code == 200

    def test_regular_user_cannot_delete(self, client, user_headers, another_user):
        response = client.delete(f"/api/users/{another_user.id}", headers=user_headers)
        assert response.status_code == 403

    def test_delete_nonexistent_user(self, client, admin_headers):
        response = client.delete("/api/users/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_deleted_user_not_found_after_deletion(self, client, admin_headers, regular_user):
        client.delete(f"/api/users/{regular_user.id}", headers=admin_headers)
        response = client.get(f"/api/users/{regular_user.id}", headers=admin_headers)
        assert response.status_code == 404
