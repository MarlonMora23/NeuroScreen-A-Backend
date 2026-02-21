from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User, UserRole


class UserService:

    @staticmethod
    def create_user(data: dict, current_user: User):
        if current_user.role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can create users")

        required_fields = ["email", "password", "first_name", "last_name"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        email = data["email"].strip().lower()

        # Basic email format validation
        if "@" not in email or "." not in email:
            raise ValueError("Invalid email format")

        # Basic password strength validation
        password = data["password"]
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        first_name = data["first_name"].strip()
        last_name = data["last_name"].strip()
        if not first_name:
            raise ValueError("First name cannot be empty")
        if not last_name:
            raise ValueError("Last name cannot be empty")

        if User.query.filter_by(email=email).first():
            raise ValueError("Email already registered")

        role_str = data.get("role", "USER").upper()
        if role_str not in UserRole.__members__:
            raise ValueError("Invalid role")

        role = UserRole[role_str]

        user = User(
            email=email,
            password_hash=generate_password_hash(data["password"]),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        db.session.add(user)
        db.session.commit()

        return UserService._to_dict(user)

    @staticmethod
    def list_users(current_user: User):
        if current_user.role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can list users")

        users = db.session.query(User).filter_by(is_deleted=False).all()
        return [UserService._to_dict(u) for u in users]

    @staticmethod
    def get_user(user_id: int, current_user: User):
        user = db.session.get(User, user_id)
        if not user or user.is_deleted:
            raise ValueError("User not found")

        # ADMIN can see any user
        # USER can only see itself
        if current_user.role != UserRole.ADMIN and current_user.id != user.id:
            raise PermissionError("Not allowed to view this user")

        return UserService._to_dict(user)

    @staticmethod
    def update_user(user_id: int, data: dict, current_user: User):
        user = db.session.get(User, user_id)
        if not user or user.is_deleted:
            raise ValueError("User not found")

        # ADMIN can update any user
        # USER can only update itself
        if current_user.role != UserRole.ADMIN and current_user.id != user.id:
            raise PermissionError("Not allowed to update this user")

        # Rol is read-only
        if "role" in data:
            raise ValueError("Role cannot be updated")

        if "email" in data:
            email = data["email"].strip().lower()

            existing = User.query.filter(
                User.email == email,
                User.id != user_id
            ).first()

            if existing:
                raise ValueError("Email already registered")

            user.email = email

        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)

        db.session.commit()
        return UserService._to_dict(user)

    @staticmethod
    def delete_user(user_id: int, current_user: User):
        user = db.session.get(User, user_id)
        if not user or user.is_deleted:
            raise ValueError("User not found")

        if current_user.role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can delete users")

        user.soft_delete()
        db.session.commit()

        return UserService._to_dict(user)

    @staticmethod
    def _to_dict(user: User):
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
