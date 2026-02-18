from app.extensions import db
from datetime import datetime, timezone

class AuditMixin(db.Model):
    """Track creation and modification times"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),     
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class BaseModel(AuditMixin):
    """Track traceability + soft delete"""
    __abstract__ = True

    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)