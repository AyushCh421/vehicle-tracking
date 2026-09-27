"""
Core GPS ingestion logic, shared by the MQTT listener (and reusable from
any future HTTP ingestion endpoint).
"""
from datetime import datetime, timezone
import logging

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.gps import GPSTracking
from app.schemas.gps import GPSMessage
from app.services.vehicle_service import refresh_vehicle_status

logger = logging.getLogger("gps_service")


def ingest_gps_reading(vehicle_id: int, message: GPSMessage, db: Session | None = None) -> bool:
    """
    Validate the vehicle exists, store the historical record, and update
    the vehicle's denormalized latest-location fields.

    Returns True if the reading was stored, False if the vehicle id is unknown.
    """
    owns_session = db is None
    db = db or SessionLocal()
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            logger.warning("Rejected GPS message for unknown vehicle_id=%s", vehicle_id)
            return False

        ts = message.timestamp or datetime.now(timezone.utc)

        record = GPSTracking(
            vehicle_id=vehicle_id,
            latitude=message.latitude,
            longitude=message.longitude,
            speed=message.speed,
            timestamp=ts,
        )
        db.add(record)

        vehicle.latest_latitude = message.latitude
        vehicle.latest_longitude = message.longitude
        vehicle.latest_speed = message.speed
        vehicle.latest_gps_timestamp = ts
        refresh_vehicle_status(vehicle)

        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        if owns_session:
            db.close()
