from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.vehicle import Vehicle
from app.models.gps import GPSTracking
from app.models.user import User


def get_vehicle_for_user(db: Session, user: User) -> Vehicle | None:
    """
    Authorization boundary: a user may only ever see the vehicle referenced
    by their own vehicle_id. There is no vehicle-by-arbitrary-id endpoint,
    so a request for another user's vehicle has no way to be expressed.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == user.vehicle_id).first()
    if vehicle:
        refresh_vehicle_status(vehicle)
    return vehicle


def refresh_vehicle_status(vehicle: Vehicle) -> Vehicle:
    """Recompute ACTIVE/OFFLINE based on how recently GPS data arrived."""
    if vehicle.latest_gps_timestamp is None:
        vehicle.status = "OFFLINE"
        return vehicle

    last_ts = vehicle.latest_gps_timestamp
    if last_ts.tzinfo is None:
        last_ts = last_ts.replace(tzinfo=timezone.utc)

    age_seconds = (datetime.now(timezone.utc) - last_ts).total_seconds()
    vehicle.status = "ACTIVE" if age_seconds <= settings.OFFLINE_THRESHOLD_SECONDS else "OFFLINE"
    return vehicle


def get_history_for_user(
    db: Session,
    user: User,
    limit: int = 100,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
) -> list[GPSTracking]:
    query = db.query(GPSTracking).filter(GPSTracking.vehicle_id == user.vehicle_id)

    if from_ts is not None:
        query = query.filter(GPSTracking.timestamp >= from_ts)
    if to_ts is not None:
        query = query.filter(GPSTracking.timestamp <= to_ts)

    return query.order_by(GPSTracking.timestamp.desc()).limit(limit).all()
