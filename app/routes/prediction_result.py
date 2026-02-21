from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.utils.security import get_current_user
from app.services.prediction_result_service import PredictionResultService

predictions_bp = Blueprint("predictions", __name__)


@predictions_bp.route("/eeg-records/<int:eeg_record_id>/prediction", methods=["GET"])
@jwt_required()
def get_prediction_by_eeg(eeg_record_id):
    """
    Returns the prediction result associated with a specific EEG.
    Returns 404 if the EEG does not exist, is not processed, or failed.
    """
    try:
        current_user = get_current_user()
        prediction = PredictionResultService.get_by_eeg_record(
            eeg_record_id, current_user
        )
        return jsonify(prediction), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@predictions_bp.route("/patients/<int:patient_id>/predictions", methods=["GET"])
@jwt_required()
def list_predictions_by_patient(patient_id):
    """
    Complete history of a patient's predictions. 
    The user only sees their own patients' predictions; the administrator sees all predictions.
    """
    try:
        current_user = get_current_user()
        predictions = PredictionResultService.list_by_patient(
            patient_id, current_user
        )
        return jsonify(predictions), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@predictions_bp.route("/predictions", methods=["GET"])
@jwt_required()
def list_all_predictions():
    """
    ADMIN only. Global view of all system predictions.
    """
    try:
        current_user = get_current_user()
        predictions = PredictionResultService.list_all(current_user)
        return jsonify(predictions), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403