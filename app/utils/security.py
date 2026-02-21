from flask import request
from flask_jwt_extended import get_jwt, get_current_user as jwt_get_current_user
from app.extensions import jwt
from app.services.auth_service import AuthService


def get_current_user():
    return jwt_get_current_user()


def register_jwt_callbacks(app):

    @jwt.token_in_blocklist_loader
    def check_token_in_blocklist(jwt_header, jwt_data):
        """
        Flask-JWT-Extended calls this on every request with @jwt_required().
        If it returns True, the token is automatically rejected with a 401 error.
        """
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return True

        is_valid = AuthService.validate_session(token)

        if is_valid:
            # Refresh expiration on each active request (sliding window)
            AuthService.refresh_session(token)

        return not is_valid

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        from flask import jsonify
        return jsonify({"error": "Session expired or revoked. Please log in again."}), 401