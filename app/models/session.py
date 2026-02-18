from app.extensions import db
from app.models.base import AuditMixin

class Session(AuditMixin):
    __tablename__ = "sessions"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    token = db.Column(db.String(500), unique=True, index=True, nullable=False)

    start_date = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False)