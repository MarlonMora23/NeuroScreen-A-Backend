import pytest


class TestCreatePatient:

    def test_create_patient_success(self, client, user_headers):
        response = client.post("/api/patients", json={
            "identification_number": "987654321",
            "first_name": "Ana",
            "last_name": "Martínez",
            "birth_date": "1985-03-15"
        }, headers=user_headers)
        data = response.get_json()
        assert response.status_code == 201
        assert data["identification_number"] == "987654321"
        assert data["birth_date"] == "1985-03-15"

    def test_create_patient_without_birthdate(self, client, user_headers):
        response = client.post("/api/patients", json={
            "identification_number": "111222333",
            "first_name": "Sin",
            "last_name": "Fecha"
        }, headers=user_headers)
        assert response.status_code == 201
        assert response.get_json()["birth_date"] is None

    def test_create_patient_duplicate_identification(self, client, user_headers, sample_patient):
        response = client.post("/api/patients", json={
            "identification_number": "123456789",  # ya existe en sample_patient
            "first_name": "Duplicado",
            "last_name": "Test"
        }, headers=user_headers)
        assert response.status_code == 400

    def test_create_patient_missing_fields(self, client, user_headers):
        response = client.post("/api/patients", json={
            "first_name": "Solo"
        }, headers=user_headers)
        assert response.status_code == 400

    def test_create_patient_invalid_birth_date(self, client, user_headers):
        response = client.post("/api/patients", json={
            "identification_number": "444555666",
            "first_name": "Fecha",
            "last_name": "Invalida",
            "birth_date": "15-03-1985"  # formato incorrecto
        }, headers=user_headers)
        assert response.status_code == 400

    def test_create_patient_requires_auth(self, client):
        response = client.post("/api/patients", json={
            "identification_number": "000111222",
            "first_name": "Sin",
            "last_name": "Auth"
        })
        assert response.status_code == 401


class TestListPatients:

    def test_user_sees_only_own_patients(self, client, user_headers, another_user_headers, sample_patient):
        # sample_patient pertenece a regular_user
        response = client.get("/api/patients", headers=another_user_headers)
        ids = [p["id"] for p in response.get_json()]
        assert sample_patient.id not in ids

    def test_admin_sees_all_patients(self, client, admin_headers, sample_patient):
        response = client.get("/api/patients", headers=admin_headers)
        assert response.status_code == 200
        ids = [p["id"] for p in response.get_json()]
        assert sample_patient.id in ids

    def test_list_excludes_deleted_patients(self, client, admin_headers, sample_patient):
        client.delete(f"/api/patients/{sample_patient.id}", headers=admin_headers)
        response = client.get("/api/patients", headers=admin_headers)
        ids = [p["id"] for p in response.get_json()]
        assert sample_patient.id not in ids


class TestGetPatient:

    def test_user_can_get_own_patient(self, client, user_headers, sample_patient):
        response = client.get(f"/api/patients/{sample_patient.id}", headers=user_headers)
        assert response.status_code == 200
        assert response.get_json()["id"] == sample_patient.id

    def test_user_cannot_get_another_users_patient(self, client, another_user_headers, sample_patient):
        response = client.get(f"/api/patients/{sample_patient.id}", headers=another_user_headers)
        assert response.status_code == 403

    def test_admin_can_get_any_patient(self, client, admin_headers, sample_patient):
        response = client.get(f"/api/patients/{sample_patient.id}", headers=admin_headers)
        assert response.status_code == 200

    def test_get_nonexistent_patient(self, client, user_headers):
        response = client.get("/api/patients/99999", headers=user_headers)
        assert response.status_code == 404

    def test_get_deleted_patient_returns_404(self, client, admin_headers, sample_patient):
        client.delete(f"/api/patients/{sample_patient.id}", headers=admin_headers)
        response = client.get(f"/api/patients/{sample_patient.id}", headers=admin_headers)
        assert response.status_code == 404


class TestUpdatePatient:

    def test_user_can_update_own_patient(self, client, user_headers, sample_patient):
        response = client.put(f"/api/patients/{sample_patient.id}", json={
            "first_name": "NuevoNombre"
        }, headers=user_headers)
        assert response.status_code == 200
        assert response.get_json()["first_name"] == "NuevoNombre"

    def test_cannot_update_identification_number(self, client, user_headers, sample_patient):
        response = client.put(f"/api/patients/{sample_patient.id}", json={
            "identification_number": "000000000"
        }, headers=user_headers)
        assert response.status_code == 400

    def test_user_cannot_update_another_users_patient(self, client, another_user_headers, sample_patient):
        response = client.put(f"/api/patients/{sample_patient.id}", json={
            "first_name": "Hack"
        }, headers=another_user_headers)
        assert response.status_code == 403

    def test_update_with_invalid_birth_date(self, client, user_headers, sample_patient):
        response = client.put(f"/api/patients/{sample_patient.id}", json={
            "birth_date": "no-es-fecha"
        }, headers=user_headers)
        assert response.status_code == 400


class TestDeletePatient:

    def test_user_can_delete_own_patient(self, client, user_headers, sample_patient):
        response = client.delete(f"/api/patients/{sample_patient.id}", headers=user_headers)
        assert response.status_code == 200

    def test_user_cannot_delete_another_users_patient(self, client, another_user_headers, sample_patient):
        response = client.delete(f"/api/patients/{sample_patient.id}", headers=another_user_headers)
        assert response.status_code == 403

    def test_admin_can_delete_any_patient(self, client, admin_headers, sample_patient):
        response = client.delete(f"/api/patients/{sample_patient.id}", headers=admin_headers)
        assert response.status_code == 200

    def test_delete_nonexistent_patient(self, client, user_headers):
        response = client.delete("/api/patients/99999", headers=user_headers)
        assert response.status_code == 404
