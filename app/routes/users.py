from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.user_service import UserService
from app.utils.security import get_current_user

users_bp = Blueprint("users", __name__)

@users_bp.route("/users", methods=["POST"])
@jwt_required()
def create_user():
    data = request.get_json() or {}

    try:
        current_user = get_current_user()
        user = UserService.create_user(data, current_user)
        return jsonify(user), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    try:
        current_user = get_current_user()
        users = UserService.list_users(current_user)
        return jsonify(users), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@users_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    try:
        current_user = get_current_user()
        user = UserService.get_user(user_id, current_user)
        return jsonify(user), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    
@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    data = request.get_json() or {}

    try:
        current_user = get_current_user()
        user = UserService.update_user(user_id, data, current_user)
        return jsonify(user), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    try:
        current_user = get_current_user()
        user = UserService.delete_user(user_id, current_user)
        return jsonify({"message": f"User {user['id']} deleted"}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    


