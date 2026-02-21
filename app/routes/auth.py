from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    try:
        result = AuthService.login(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        AuthService.logout(token)
        return jsonify({"message": "Session closed successfully"}), 200
    except Exception:
        return jsonify({"error": "Could not close session"}), 500


@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def me():
    from app.utils.security import get_current_user
    try:
        user = get_current_user()
        return jsonify({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }), 200
    except Exception:
        return jsonify({"error": "Could not retrieve user info"}), 500