from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.eeg_record_service import EegRecordService
from app.utils.security import get_current_user
from app.tasks.eeg_tasks import process_eeg_record

eeg_records_bp = Blueprint("eeg_records", __name__)

@eeg_records_bp.route("/eeg-records/upload", methods=["POST"])
@jwt_required()
def upload_eeg():
    try:
        current_user = get_current_user()

        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files["file"]
        patient_id = request.form.get("patient_id")

        if not patient_id:
            return jsonify({"error": "patient_id is required"}), 400

        try:
            patient_id = int(patient_id)
        except ValueError:
            return jsonify({"error": "patient_id must be an integer"}), 400

        record = EegRecordService.create_eeg_record(file, patient_id, current_user)

        # Enqueue background task passing the record ID
        process_eeg_record.delay(record["id"])

        return jsonify({
            "message": "EEG file uploaded successfully. Processing started.",
            "eeg_record_id": record["id"],
            "status": record["status"],
        }), 202

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@eeg_records_bp.route("/eeg-records", methods=["GET"])
@jwt_required()
def list_eeg_records():
    try:
        current_user = get_current_user()
        filters = {
            "patient_id": request.args.get("patient_id"),
            "status": request.args.get("status"),
        }
        records = EegRecordService.list_eeg_records(filters, current_user)
        return jsonify(records), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@eeg_records_bp.route("/eeg-records/<int:eeg_id>", methods=["GET"])
@jwt_required()
def get_eeg_record(eeg_id):
    try:
        current_user = get_current_user()
        record = EegRecordService.get_eeg_record(eeg_id, current_user)
        return jsonify(record), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@eeg_records_bp.route("/patients/<int:patient_id>/eeg-records", methods=["GET"])
@jwt_required()
def list_by_patient(patient_id):
    try:
        current_user = get_current_user()
        records = EegRecordService.list_by_patient(patient_id, current_user)
        return jsonify(records), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    
@eeg_records_bp.route("/eeg-records/<int:eeg_id>/status", methods=["GET"])
@jwt_required()
def get_eeg_status(eeg_id):
    try:
        current_user = get_current_user()
        status = EegRecordService.get_eeg_status(eeg_id, current_user)
        return jsonify(status), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    
@eeg_records_bp.route("/eeg-records/<int:eeg_id>", methods=["DELETE"])
@jwt_required()
def delete_eeg_record(eeg_id):
    try:
        current_user = get_current_user()
        result = EegRecordService.delete_eeg_record(eeg_id, current_user)
        return jsonify({"message": f"EEG record {result['id']} deleted"}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
