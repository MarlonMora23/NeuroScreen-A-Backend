from app.extensions import db
from app.models.base import BaseModel
import enum

class EegStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class FILE_TYPE(enum.Enum):
    PARQUET = "parquet"
    CSV = "csv"
    JSON = "json"
    EDF = "edf"

class EegRecord(BaseModel):
    __tablename__ = "eeg_records"

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        index=True,
        nullable=False
    )

    uploader_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    file_name = db.Column(db.String(120), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.Enum(FILE_TYPE), nullable=False)
    file_size_bytes = db.Column(db.BigInteger, nullable=True)

    status = db.Column(db.Enum(EegStatus), default=EegStatus.PENDING, nullable=False)

    error_msg = db.Column(db.Text, nullable=True)

    processing_time_ms = db.Column(db.Integer, nullable=True)

    prediction_result = db.relationship("PredictionResult", backref="eeg_record", lazy=True, uselist=False)