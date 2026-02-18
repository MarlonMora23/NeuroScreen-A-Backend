from app.extensions import db
from app.models.base import BaseModel
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(BaseModel):
    __tablename__ = "users"

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)

    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)

    last_login = db.Column(db.DateTime, nullable=True)

    patients = db.relationship("Patient", backref="user", lazy=True)
    eeg_uploads = db.relationship("EegRecord", backref="uploaded_by_user", lazy=True)
    sessions = db.relationship("Session", backref="user", lazy=True)