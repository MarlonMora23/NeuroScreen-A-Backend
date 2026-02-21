import os
import uuid
from app.extensions import db
from app.models.eeg_record import EegRecord, EegStatus, FILE_TYPE
from app.models.patient import Patient
from app.models.user import User, UserRole

UPLOAD_FOLDER = "uploads/eeg"
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB
ALLOWED_EXTENSIONS = {FILE_TYPE.PARQUET: ".parquet"}

class EegRecordService:

    @staticmethod
    def create_eeg_record(file, patient_id: int, current_user: User) -> dict:
        patient = db.session.get(Patient, patient_id)
        if not patient or patient.is_deleted:
            raise ValueError("Patient not found")

        if (
            current_user.role != UserRole.ADMIN
            and patient.created_by != current_user.id
        ):
            raise PermissionError("Not allowed to upload EEG for this patient")

        # Validate name and extension
        original_filename = file.filename
        if not original_filename:
            raise ValueError("No file provided")

        ext = os.path.splitext(original_filename)[1].lower()
        allowed_exts = list(ALLOWED_EXTENSIONS.values())
        if ext not in allowed_exts:
            raise ValueError(f"File type not allowed. Allowed: {', '.join(allowed_exts)}")

        # Determine EegFileType from the extension
        file_type = next(
            (ft for ft, e in ALLOWED_EXTENSIONS.items() if e == ext),
            None
        )

        # Validate file size (read a chunk to determine if it's empty or too large)
        file.seek(0, 2)  # Go to end of file
        file_size = file.tell()
        file.seek(0)     # Go back to start

        if file_size == 0:
            raise ValueError("File is empty")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB")

        # Generate a unique name to avoid collisions and not expose the original name
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(save_path)

        record = EegRecord(
            patient_id=patient_id,
            uploader_id=current_user.id,
            file_name=original_filename,   # original name to show to users
            file_path=save_path,           # internal route, never exposed to users
            file_type=file_type,
            file_size_bytes=file_size,
            status=EegStatus.PENDING,
        )

        db.session.add(record)
        db.session.commit()

        return EegRecordService._to_dict(record)

    @staticmethod
    def list_eeg_records(filters: dict, current_user: User) -> list:
        query = EegRecord.query.filter_by(is_deleted=False)

        if current_user.role != UserRole.ADMIN:
            query = query.filter_by(uploader_id=current_user.id)

        if filters.get("patient_id"):
            try:
                patient_id = int(filters["patient_id"])
            except (ValueError, TypeError):
                raise ValueError("patient_id must be an integer")
            query = query.filter_by(patient_id=patient_id)

        if filters.get("status"):
            try:
                status = EegStatus(filters["status"])
            except ValueError:
                valid = [s.value for s in EegStatus]
                raise ValueError(f"Invalid status. Valid values: {', '.join(valid)}")
            query = query.filter_by(status=status)

        records = query.order_by(EegRecord.created_at.desc()).all()
        return [EegRecordService._to_dict(r) for r in records]
    
    @staticmethod
    def get_eeg_record(eeg_id: int, current_user: User) -> dict:
        eeg = db.session.get(EegRecord, eeg_id)

        if not eeg or eeg.is_deleted:
            raise ValueError("EEG record not found")

        if (
            current_user.role != UserRole.ADMIN
            and eeg.uploader_id != current_user.id
        ):
            raise PermissionError("Not allowed to access this record")

        return EegRecordService._to_dict(eeg)

    @staticmethod
    def list_by_patient(patient_id: int, current_user: User) -> list:
        patient = db.session.get(Patient, patient_id)
        if not patient or patient.is_deleted:
            raise ValueError("Patient not found")

        if (
            current_user.role != UserRole.ADMIN
            and patient.created_by != current_user.id
        ):
            raise PermissionError("Not allowed to access this patient's records")

        query = (
            EegRecord.query
            .filter_by(patient_id=patient_id, is_deleted=False)
            .order_by(EegRecord.created_at.desc())
        )

        if current_user.role != UserRole.ADMIN:
            query = query.filter_by(uploader_id=current_user.id)

        return [EegRecordService._to_dict(r) for r in query.all()]
    
    @staticmethod
    def get_eeg_status(eeg_id: int, current_user: User) -> dict:
        eeg = db.session.get(EegRecord, eeg_id)

        if not eeg or eeg.is_deleted:
            raise ValueError("EEG record not found")

        if (
            current_user.role != UserRole.ADMIN
            and eeg.uploader_id != current_user.id
        ):
            raise PermissionError("Not allowed to access this record")

        return {
            "id": eeg.id,
            "status": eeg.status.value,
            "processing_time_ms": eeg.processing_time_ms,
            "error_msg": eeg.error_msg if eeg.status == EegStatus.FAILED else None,
        }
    
    @staticmethod
    def delete_eeg_record(eeg_id: int, current_user: User) -> dict:
        eeg = db.session.get(EegRecord, eeg_id)

        if not eeg or eeg.is_deleted:
            raise ValueError("EEG record not found")

        if (
            current_user.role != UserRole.ADMIN
            and eeg.uploader_id != current_user.id
        ):
            raise PermissionError("Not allowed to delete this record")

        if eeg.status == EegStatus.PROCESSING:
            raise ValueError("Cannot delete a record that is currently being processed")

        eeg.soft_delete()
        db.session.commit()

        return {"id": eeg.id, "status": "deleted"}

    @staticmethod
    def _to_dict(record: EegRecord) -> dict:
        return {
            "id": record.id,
            "patient_id": record.patient_id,
            "uploader_id": record.uploader_id,
            "file_name": record.file_name,
            "file_type": record.file_type.value,
            "file_size_bytes": record.file_size_bytes,
            "status": record.status.value,
            "error_msg": record.error_msg,
            "processing_time_ms": record.processing_time_ms,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
        }