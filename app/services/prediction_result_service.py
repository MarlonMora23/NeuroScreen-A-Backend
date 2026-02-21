from app.extensions import db
from app.models.prediction_result import PredictionResult
from app.models.eeg_record import EegRecord, EegStatus
from app.models.patient import Patient
from app.models.user import User, UserRole


class PredictionResultService:

    @staticmethod
    def get_by_eeg_record(eeg_record_id: int, current_user: User) -> dict:
        eeg = db.session.get(EegRecord, eeg_record_id)
        if not eeg or eeg.is_deleted:
            raise ValueError("EEG record not found")

        if (
            current_user.role != UserRole.ADMIN
            and eeg.uploader_id != current_user.id
        ):
            raise PermissionError("Not allowed to access this record")

        # Verify that the EEG has been processed successfully before trying to get the prediction
        if eeg.status == EegStatus.PENDING or eeg.status == EegStatus.PROCESSING:
            raise ValueError("EEG record has not been processed yet")

        if eeg.status == EegStatus.FAILED:
            raise ValueError("EEG processing failed — no prediction available")

        prediction = PredictionResult.query.filter_by(
            eeg_record_id=eeg_record_id
        ).first()

        if not prediction:
            raise ValueError("Prediction result not found")

        return PredictionResultService._to_dict(prediction)

    @staticmethod
    def list_by_patient(patient_id: int, current_user: User) -> list:
        patient = db.session.get(Patient, patient_id)
        if not patient or patient.is_deleted:
            raise ValueError("Patient not found")

        if (
            current_user.role != UserRole.ADMIN
            and patient.created_by != current_user.id
        ):
            raise PermissionError("Not allowed to access this patient's predictions")

        query = (
            db.session.query(PredictionResult)
            .join(EegRecord, PredictionResult.eeg_record_id == EegRecord.id)
            .filter(
                EegRecord.patient_id == patient_id,
                EegRecord.is_deleted == False,
            )
        )

        if current_user.role != UserRole.ADMIN:
            query = query.filter(EegRecord.uploader_id == current_user.id)

        query = query.order_by(PredictionResult.created_at.desc())

        return [PredictionResultService._to_dict(p) for p in query.all()]

    @staticmethod
    def list_all(current_user: User) -> list:
        if current_user.role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can access the full predictions list")

        predictions = (
            db.session.query(PredictionResult)
            .join(EegRecord, PredictionResult.eeg_record_id == EegRecord.id)
            .filter(EegRecord.is_deleted == False)
            .order_by(PredictionResult.created_at.desc())
            .all()
        )

        return [PredictionResultService._to_dict(p) for p in predictions]

    @staticmethod
    def _to_dict(prediction: PredictionResult) -> dict:
        return {
            "id": prediction.id,
            "eeg_record_id": prediction.eeg_record_id,
            "result": prediction.result,
            "confidence": float(prediction.confidence),
            "raw_probability": (
                float(prediction.raw_probability)
                if prediction.raw_probability is not None else None
            ),
            "model_version": prediction.model_version,
            "created_at": prediction.created_at.isoformat(),
        }