from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
celery = Celery()

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"message": "Invalid token"}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"message": "Missing token"}, 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"message": "Token expired"}, 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"message": "Token revoked"}, 401
