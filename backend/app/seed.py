"""
Idempotent demo-data seeder: creates two routes, two vehicles, their
route points, and two users (user1/user2) so the assessment can be run
end-to-end immediately after `docker compose up`.

Run automatically by the backend container's CMD, or manually:
    python -m app.seed
"""
import logging

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.route import Route, RoutePoint
from app.models.vehicle import Vehicle
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

# Two short routes around Gangtok, Sikkim, as example coordinates.
ROUTE_A_POINTS = [
    (27.3389, 88.6065), (27.3400, 88.6080), (27.3415, 88.6100),
    (27.3430, 88.6120), (27.3445, 88.6140),
]
ROUTE_B_POINTS = [
    (27.3200, 88.6200), (27.3220, 88.6215), (27.3240, 88.6230),
    (27.3260, 88.6245), (27.3280, 88.6260),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            logger.info("Database already seeded, skipping.")
            return

        route_a = Route(name="Route A", route_number="R-A", description="Campus to City")
        route_b = Route(name="Route B", route_number="R-B", description="Campus to Airport")
        db.add_all([route_a, route_b])
        db.flush()

        for seq, (lat, lon) in enumerate(ROUTE_A_POINTS, start=1):
            db.add(RoutePoint(route_id=route_a.id, latitude=lat, longitude=lon, sequence_number=seq))
        for seq, (lat, lon) in enumerate(ROUTE_B_POINTS, start=1):
            db.add(RoutePoint(route_id=route_b.id, latitude=lat, longitude=lon, sequence_number=seq))

        vehicle_1 = Vehicle(
            vehicle_number="BUS-001", registration_number="SK01AB1234",
            vehicle_type="bus", status="OFFLINE", route_id=route_a.id,
        )
        vehicle_2 = Vehicle(
            vehicle_number="BUS-002", registration_number="SK01AB5678",
            vehicle_type="bus", status="OFFLINE", route_id=route_b.id,
        )
        db.add_all([vehicle_1, vehicle_2])
        db.flush()

        user_1 = User(
            username="user1", email="user1@example.com",
            password_hash=hash_password("password1"), full_name="User One",
            route_id=route_a.id, vehicle_id=vehicle_1.id,
        )
        user_2 = User(
            username="user2", email="user2@example.com",
            password_hash=hash_password("password2"), full_name="User Two",
            route_id=route_b.id, vehicle_id=vehicle_2.id,
        )
        db.add_all([user_1, user_2])

        db.commit()
        logger.info("Seeded: user1/password1 -> BUS-001 (Route A), user2/password2 -> BUS-002 (Route B)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
