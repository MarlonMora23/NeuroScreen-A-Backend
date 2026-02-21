from flask import Blueprint

api_bp = Blueprint("routes_api", __name__)

from .users import users_bp
from .auth import auth_bp
from .patients import patients_bp
from .eeg_records import eeg_records_bp
from .prediction_result import predictions_bp

api_bp.register_blueprint(users_bp)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(patients_bp)
api_bp.register_blueprint(eeg_records_bp)
api_bp.register_blueprint(predictions_bp)
