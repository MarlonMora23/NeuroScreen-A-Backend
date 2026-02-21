import pytest
import io
import os
from werkzeug.security import generate_password_hash
from app import create_app
from app.config import TestingConfig
from app.extensions import db as _db
from app.models.user import User, UserRole
from app.models.patient import Patient


# ------------------------------------------------------------------ #
# App y BD                                                             #
# ------------------------------------------------------------------ #

@pytest.fixture(scope="session")
def app():
    """Crea la app con TestingConfig una sola vez por sesión de tests."""
    app = create_app(TestingConfig)
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def db(app):
    """
    BD limpia por cada test: recrea todas las tablas antes de cada test
    y las elimina al terminar. Necesario porque SQLite no soporta
    savepoints de forma fiable con Flask-SQLAlchemy.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    """
    El client depende de db para garantizar que la BD está lista
    antes de que cualquier request llegue a los endpoints.
    """
    with app.test_client() as c:
        with app.app_context():
            yield c


# ------------------------------------------------------------------ #
# Usuarios                                                             #
# ------------------------------------------------------------------ #

@pytest.fixture
def admin_user(db):
    user = User(
        email="admin@neuroscreen.com",
        password_hash=generate_password_hash("Admin123"),
        first_name="Admin",
        last_name="Principal",
        role=UserRole.ADMIN,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def regular_user(db):
    user = User(
        email="doctor@neuroscreen.com",
        password_hash=generate_password_hash("Doctor123"),
        first_name="Juan",
        last_name="García",
        role=UserRole.USER,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def another_user(db):
    """Segundo usuario USER para probar aislamiento entre usuarios."""
    user = User(
        email="doctor2@neuroscreen.com",
        password_hash=generate_password_hash("Doctor456"),
        first_name="María",
        last_name="López",
        role=UserRole.USER,
    )
    db.session.add(user)
    db.session.commit()
    return user


# ------------------------------------------------------------------ #
# Tokens JWT                                                           #
# ------------------------------------------------------------------ #

def get_token(client, email, password):
    response = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    return response.get_json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    return get_token(client, "admin@neuroscreen.com", "Admin123")


@pytest.fixture
def user_token(client, regular_user):
    return get_token(client, "doctor@neuroscreen.com", "Doctor123")


@pytest.fixture
def another_user_token(client, another_user):
    return get_token(client, "doctor2@neuroscreen.com", "Doctor456")


# ------------------------------------------------------------------ #
# Headers de autorización                                              #
# ------------------------------------------------------------------ #

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def another_user_headers(another_user_token):
    return {"Authorization": f"Bearer {another_user_token}"}


# ------------------------------------------------------------------ #
# Paciente de prueba                                                   #
# ------------------------------------------------------------------ #

@pytest.fixture
def sample_patient(db, regular_user):
    patient = Patient(
        identification_number="123456789",
        first_name="Carlos",
        last_name="Pérez",
        birth_date=None,
        created_by=regular_user.id,
    )
    db.session.add(patient)
    db.session.commit()
    return patient


# ------------------------------------------------------------------ #
# Archivo .parquet de prueba                                           #
# ------------------------------------------------------------------ #

PARQUET_FILE_PATH = r"C:\Users\Marlon\Downloads\co3c0000402.parquet"

@pytest.fixture
def parquet_file():
    """
    Carga el archivo .parquet real desde disco.
    Si no existe, crea un parquet mínimo válido en memoria para no bloquear
    los tests que no necesitan el modelo de ML.
    """
    if os.path.exists(PARQUET_FILE_PATH):
        with open(PARQUET_FILE_PATH, "rb") as f:
            data = f.read()
        return (io.BytesIO(data), "co3c0000402.parquet")

    # Fallback: parquet mínimo sintético (solo para tests de upload/validación)
    import pandas as pd
    import numpy as np

    df = pd.DataFrame({
        "trial": np.repeat(np.arange(5), 256 * 10),
        "channel": np.tile(
            np.repeat(["F1", "F2", "O1", "C1", "T7"], 256),
            5
        ),
        "sample": np.tile(np.arange(256), 5 * 10),
        "value": np.random.randn(5 * 256 * 10).astype(np.float32),
    })

    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    return (buffer, "synthetic_eeg.parquet")