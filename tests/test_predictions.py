import pytest


def upload_and_get_prediction_id(client, headers, patient_id, parquet_file):
    """Helper: sube un EEG y devuelve el eeg_record_id."""
    file_data, filename = parquet_file
    r = client.post(
        "/api/eeg-records/upload",
        data={
            "patient_id": str(patient_id),
            "file": (file_data, filename, "application/octet-stream")
        },
        headers=headers,
        content_type="multipart/form-data"
    )
    return r.get_json()["eeg_record_id"]


class TestGetPrediction:

    def test_prediction_available_after_processing(
        self, client, user_headers, sample_patient, parquet_file
    ):
        """Con CELERY_TASK_ALWAYS_EAGER la tarea ya habrá corrido al hacer el upload."""
        eeg_id = upload_and_get_prediction_id(
            client, user_headers, sample_patient.id, parquet_file
        )

        # Verificar que el estado es terminal
        status_r = client.get(f"/api/eeg-records/{eeg_id}/status", headers=user_headers)
        status = status_r.get_json()["status"]

        if status == "processed":
            response = client.get(
                f"/api/eeg-records/{eeg_id}/prediction",
                headers=user_headers
            )
            data = response.get_json()
            assert response.status_code == 200
            assert "result" in data
            assert "confidence" in data
            assert "model_version" in data
            assert 0.0 <= float(data["confidence"]) <= 1.0

    def test_prediction_not_available_for_nonexistent_record(self, client, user_headers):
        response = client.get("/api/eeg-records/99999/prediction", headers=user_headers)
        assert response.status_code == 404

    def test_user_cannot_get_another_users_prediction(
        self, client, user_headers, another_user_headers, sample_patient, parquet_file
    ):
        eeg_id = upload_and_get_prediction_id(
            client, user_headers, sample_patient.id, parquet_file
        )
        response = client.get(
            f"/api/eeg-records/{eeg_id}/prediction",
            headers=another_user_headers
        )
        assert response.status_code == 403

    def test_admin_can_get_any_prediction(
        self, client, admin_headers, user_headers, sample_patient, parquet_file
    ):
        eeg_id = upload_and_get_prediction_id(
            client, user_headers, sample_patient.id, parquet_file
        )
        status_r = client.get(f"/api/eeg-records/{eeg_id}/status", headers=admin_headers)
        if status_r.get_json()["status"] == "processed":
            response = client.get(
                f"/api/eeg-records/{eeg_id}/prediction",
                headers=admin_headers
            )
            assert response.status_code == 200

    def test_prediction_does_not_expose_file_path(
        self, client, user_headers, sample_patient, parquet_file
    ):
        eeg_id = upload_and_get_prediction_id(
            client, user_headers, sample_patient.id, parquet_file
        )
        status_r = client.get(f"/api/eeg-records/{eeg_id}/status", headers=user_headers)
        if status_r.get_json()["status"] == "processed":
            response = client.get(
                f"/api/eeg-records/{eeg_id}/prediction",
                headers=user_headers
            )
            assert "file_path" not in response.get_json()

    def test_prediction_requires_auth(self, client):
        response = client.get("/api/eeg-records/1/prediction")
        assert response.status_code == 401


class TestListPredictionsByPatient:

    def test_list_predictions_by_patient(
        self, client, user_headers, sample_patient, parquet_file
    ):
        upload_and_get_prediction_id(client, user_headers, sample_patient.id, parquet_file)
        response = client.get(
            f"/api/patients/{sample_patient.id}/predictions",
            headers=user_headers
        )
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)

    def test_user_cannot_list_predictions_of_another_users_patient(
        self, client, another_user_headers, sample_patient
    ):
        response = client.get(
            f"/api/patients/{sample_patient.id}/predictions",
            headers=another_user_headers
        )
        assert response.status_code == 403

    def test_list_predictions_deleted_patient_returns_404(
        self, client, admin_headers, sample_patient
    ):
        client.delete(f"/api/patients/{sample_patient.id}", headers=admin_headers)
        response = client.get(
            f"/api/patients/{sample_patient.id}/predictions",
            headers=admin_headers
        )
        assert response.status_code == 404


class TestListAllPredictions:

    def test_admin_can_list_all_predictions(self, client, admin_headers):
        response = client.get("/api/predictions", headers=admin_headers)
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)

    def test_regular_user_cannot_list_all_predictions(self, client, user_headers):
        response = client.get("/api/predictions", headers=user_headers)
        assert response.status_code == 403

    def test_list_all_requires_auth(self, client):
        response = client.get("/api/predictions")
        assert response.status_code == 401
