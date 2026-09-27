"""
Basic tests using an in-memory SQLite DB to verify:
- login works and returns a JWT
- a user can only ever see their own route/vehicle/location (never another user's)
"""
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.route import Route, RoutePoint
from app.models.vehicle import Vehicle
from app.models.user import User

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()

    route_a = Route(name="Route A", route_number="R-A")
    route_b = Route(name="Route B", route_number="R-B")
    db.add_all([route_a, route_b])
    db.flush()

    vehicle_1 = Vehicle(vehicle_number="BUS-001", registration_number="SK01", route_id=route_a.id)
    vehicle_2 = Vehicle(vehicle_number="BUS-002", registration_number="SK02", route_id=route_b.id)
    db.add_all([vehicle_1, vehicle_2])
    db.flush()

    db.add(RoutePoint(route_id=route_a.id, latitude=27.1, longitude=88.1, sequence_number=1))

    db.add(User(
        username="user1", email="u1@example.com", password_hash=hash_password("pw1"),
        full_name="User One", route_id=route_a.id, vehicle_id=vehicle_1.id,
    ))
    db.add(User(
        username="user2", email="u2@example.com", password_hash=hash_password("pw2"),
        full_name="User Two", route_id=route_b.id, vehicle_id=vehicle_2.id,
    ))
    db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _login(username, password):
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_login_success():
    token = _login("user1", "pw1")
    assert token


def test_login_failure():
    resp = client.post("/api/auth/login", data={"username": "user1", "password": "wrong"})
    assert resp.status_code == 401


def test_user_sees_only_own_vehicle_and_route():
    token1 = _login("user1", "pw1")
    headers1 = {"Authorization": f"Bearer {token1}"}

    vehicle_resp = client.get("/api/vehicles/me", headers=headers1)
    assert vehicle_resp.status_code == 200
    assert vehicle_resp.json()["vehicle_number"] == "BUS-001"

    route_resp = client.get("/api/routes/me", headers=headers1)
    assert route_resp.status_code == 200
    assert route_resp.json()["route_number"] == "R-A"

    token2 = _login("user2", "pw2")
    headers2 = {"Authorization": f"Bearer {token2}"}

    vehicle_resp_2 = client.get("/api/vehicles/me", headers=headers2)
    assert vehicle_resp_2.json()["vehicle_number"] == "BUS-002"
    assert vehicle_resp_2.json()["vehicle_number"] != vehicle_resp.json()["vehicle_number"]


def test_no_auth_is_rejected():
    resp = client.get("/api/vehicles/me")
    assert resp.status_code == 401
