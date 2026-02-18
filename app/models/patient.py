from app.extensions import db
from app.models.base import BaseModel

class Patient(BaseModel):
    __tablename__ = "patients"

    identification_number = db.Column(db.String(20), unique=True, index=True, nullable=False)

    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)

    birth_date = db.Column(db.Date, nullable=True)
    
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    eeg_records = db.relationship("EegRecord", backref="patient", lazy=True)