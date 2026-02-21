from flask import Flask
from .config import Config, TestingConfig
from .extensions import db, migrate, jwt
from app.models.user import User
from app.celery_app import create_celery
from app.utils.security import register_jwt_callbacks


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Config JWT serializer
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))
    
    register_jwt_callbacks(app)
    
    celery = create_celery(app)
    app.celery = celery

    from app import models
    from app.routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    return app