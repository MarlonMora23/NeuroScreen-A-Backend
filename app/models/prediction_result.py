from app.extensions import db
from app.models.base import BaseModel

class PredictionResult(BaseModel):
    __tablename__ = "prediction_results"

    eeg_record_id = db.Column(
        db.Integer,
        db.ForeignKey("eeg_records.id"),
        unique=True,
        index=True,
        nullable=False
    )

    result = db.Column(db.Boolean, nullable=False)
    confidence = db.Column(db.Numeric(5,4), nullable=False)

    model_version = db.Column(db.String(120), nullable=False)