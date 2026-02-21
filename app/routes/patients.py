from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.security import get_current_user
from app.services.patient_service import PatientService

patients_bp = Blueprint("patients", __name__)


@patients_bp.route("/patients", methods=["POST"])
@jwt_required()
def create_patient():
    data = request.get_json() or {}

    try:
        current_user = get_current_user()
        patient = PatientService.create_patient(data, current_user)
        return jsonify(patient), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@patients_bp.route("/patients", methods=["GET"])
@jwt_required()
def list_patients():
    try:
        current_user = get_current_user()

        filters = {
            "identification_number": request.args.get("identification_number"),
            "first_name": request.args.get("first_name"),
            "last_name": request.args.get("last_name"),
            "has_eeg_records": request.args.get("has_eeg_records"),
            "has_pending_eeg": request.args.get("has_pending_eeg"),
        }
        patients = PatientService.list_patients(filters, current_user)
        return jsonify(patients), 200
    
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@patients_bp.route("/patients/<int:patient_id>", methods=["GET"])
@jwt_required()
def get_patient(patient_id):
    try:
        current_user = get_current_user()
        patient = PatientService.get_patient(patient_id, current_user)
        return jsonify(patient), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@patients_bp.route("/patients/<int:patient_id>", methods=["PUT"])
@jwt_required()
def update_patient(patient_id):
    data = request.get_json() or {}

    try:
        current_user = get_current_user()
        patient = PatientService.update_patient(
            patient_id, data, current_user
        )
        return jsonify(patient), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@patients_bp.route("/patients/<int:patient_id>", methods=["DELETE"])
@jwt_required()
def delete_patient(patient_id):
    try:
        current_user = get_current_user()
        patient = PatientService.delete_patient(
            patient_id, current_user
        )
        return jsonify({"message": f"Patient {patient['id']} deleted"}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
