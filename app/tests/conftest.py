import pytest
from datetime import datetime, UTC
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db import get_db
from app.core.config import settings


# 🔹 Test DB engine
engine = create_engine(settings.TEST_DATABASE_URL, future=True)

# 🔹 Recreate tables once
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# 🔹 DB session fixture (transaction rollback)
@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# 🔹 FastAPI client with overridden DB
@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
@pytest.fixture()
def auth_headers(client, db_session):
    # register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@test.com",
            "password": "password123",
        },
    )

    # 🔥 PROMOTE TO ADMIN
    from app.models.user import User
    user = db_session.query(User).filter(User.email == "admin@test.com").first()
    user.role = "admin"
    db_session.commit()

    # login
    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@test.com",
            "password": "password123",
        },
    )

    token = login.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

    # manually promote to admin (direct DB update would be cleaner,
    # but this is OK for tests)
    # alternatively: have a test-only admin creation helper

    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@test.com",
            "password": "password123",
        },
    )

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# 🔹 MAIN BOOKING SETUP FIXTURE
@pytest.fixture()
def setup_booking_data(client, auth_headers):
    # create center
    center = client.post(
        "/api/v1/centers/",
        json={
            "name": "Test Center",
            "address": "Test Street 1",
            "city": "Ljubljana",
        },
        headers=auth_headers,
    ).json()

    # create class type
    class_type = client.post(
        "/api/v1/class-types/",
        json={
            "name": "Yoga",
            "duration": 60,
            "center_id": center["id"],
        },
        headers=auth_headers,
    ).json()

    # create session
    session = client.post(
        "/api/v1/admin/sessions",
        json={
            "center_id": center["id"],
            "class_type_id": class_type["id"],
            "start_time": datetime.now(UTC).isoformat(),
            "capacity": 1,
        },
        headers=auth_headers,
    ).json()

    # seed ticket
    client.post("/api/v1/admin/tickets/seed", headers=auth_headers)

    return {
        "headers": auth_headers,
        "center_id": center["id"],
        "class_type_id": class_type["id"],
        "session_id": session["id"],
    }