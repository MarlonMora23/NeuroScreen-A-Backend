from datetime import datetime
from app.extensions import db
from app.models.eeg_record import EegRecord
from app.models.patient import Patient
from app.models.user import User, UserRole
from sqlalchemy import func


class PatientService:

    @staticmethod
    def create_patient(data: dict, current_user: User):
        required_fields = ["identification_number", "first_name", "last_name"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        existing_patient = Patient.query.filter_by(
            identification_number=data["identification_number"]
        ).first()
        if existing_patient:
            if existing_patient.is_deleted:
                raise ValueError("A patient with this identification_number was previously deleted")
            raise ValueError("identification_number already exists")
        
        first_name = data["first_name"].strip()
        last_name = data["last_name"].strip()
        if not first_name:
            raise ValueError("First name cannot be empty")
        if not last_name:
            raise ValueError("Last name cannot be empty")

        birth_date = None
        if "birth_date" in data and data["birth_date"]:
            try:
                birth_date = datetime.strptime(
                    data["birth_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                raise ValueError("birth_date must be YYYY-MM-DD")

        patient = Patient(
            identification_number=data["identification_number"].strip(),
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            created_by=current_user.id
        )

        db.session.add(patient)
        db.session.commit()

        return PatientService._to_dict(patient)

    @staticmethod
    def list_patients(filters: dict, current_user):
        query = db.session.query(Patient).filter_by(is_deleted=False)

        # Control por rol
        if current_user.role != UserRole.ADMIN:
            query = query.filter_by(created_by=current_user.id)

        # ---- Filters ----

        # identification_number (exact)
        if filters.get("identification_number"):
            query = query.filter(
                Patient.identification_number == filters["identification_number"]
            )

        # first_name (partial, case insensitive)
        if filters.get("first_name"):
            query = query.filter(
                func.lower(Patient.first_name).like(
                    f"%{filters['first_name'].lower()}%"
                )
            )

        # last_name (partial, case insensitive)
        if filters.get("last_name"):
            query = query.filter(
                func.lower(Patient.last_name).like(
                    f"%{filters['last_name'].lower()}%"
                )
            )

        # has_eeg_records (boolean)
        if filters.get("has_eeg_records") is not None:
            if filters["has_eeg_records"] == "true":
                query = query.filter(
                    db.exists().where(EegRecord.patient_id == Patient.id)
                )
            elif filters["has_eeg_records"] == "false":
                query = query.filter(
                    ~db.exists().where(EegRecord.patient_id == Patient.id)
                )

        # has_pending_eeg (boolean)
        if filters.get("has_pending_eeg") is not None:
            if filters["has_pending_eeg"] == "true":
                query = query.filter(
                    db.exists().where(
                        (EegRecord.patient_id == Patient.id) &
                        (EegRecord.status == EegRecord.status.PENDING)
                    )
                )
            elif filters["has_pending_eeg"] == "false":
                query = query.filter(
                    ~db.exists().where(
                        (EegRecord.patient_id == Patient.id) &
                        (EegRecord.status == EegRecord.status.PENDING)
                    )
                )

        patients = query.order_by(Patient.created_at.desc()).all()

        return [PatientService._to_dict(p) for p in patients]

    @staticmethod
    def get_patient(patient_id: int, current_user):
        patient = db.session.get(Patient, patient_id)
        if not patient or patient.is_deleted:
            raise ValueError("Patient not found")

        if (
            current_user.role != UserRole.ADMIN
            and patient.created_by != current_user.id
        ):
            raise PermissionError("Not allowed to access this patient")

        return PatientService._to_dict(patient)

    @staticmethod
    def update_patient(patient_id: int, data: dict, current_user):
        patient = db.session.get(Patient, patient_id)
        if not patient or patient.is_deleted:
            raise ValueError("Patient not found")

        if (
            current_user.role != UserRole.ADMIN
            and patient.created_by != current_user.id
        ):
            raise PermissionError("Not allowed to update this patient")
        
        if "identification_number" in data:
            raise ValueError("identification_number cannot be updated")

        if "birth_date" in data:
            try:
                patient.birth_date = datetime.strptime(
                    data["birth_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                raise ValueError("birth_date must be YYYY-MM-DD")

        patient.first_name = data.get("first_name", patient.first_name)
        patient.last_name = data.get("last_name", patient.last_name)

        db.session.commit()

        return PatientService._to_dict(patient)

    @staticmethod
    def delete_patient(patient_id: int, current_user):
        patient = db.session.get(Patient, patient_id)
        if not patient or patient.is_deleted:
            raise ValueError("Patient not found")

        if (
            current_user.role != UserRole.ADMIN
            and patient.created_by != current_user.id
        ):
            raise PermissionError("Not allowed to delete this patient")

        patient.soft_delete()
        db.session.commit()

        return PatientService._to_dict(patient)

    @staticmethod
    def _to_dict(patient: Patient):
        return {
            "id": patient.id,
            "identification_number": patient.identification_number,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "birth_date": (
                patient.birth_date.isoformat()
                if patient.birth_date else None
            ),
            "created_by": patient.created_by,
            "created_at": (
                patient.created_at.isoformat()
                if patient.created_at else None
            ),
        }
