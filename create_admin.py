from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    user = User(
        email="admin@neuroscreen.com",
        password_hash=generate_password_hash("Admin123"),
        first_name="Admin",
        last_name="Principal",
        role=UserRole.ADMIN,
    )

    db.session.add(user)
    db.session.commit()

    print("Admin created")
