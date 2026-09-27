from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    registration_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(32), default="bus", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="OFFLINE", nullable=False)

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)

    # Denormalized "latest location" fields — avoids scanning gps_tracking
    # history every time the app asks for the current position.
    latest_latitude: Mapped[float] = mapped_column(Float, nullable=True)
    latest_longitude: Mapped[float] = mapped_column(Float, nullable=True)
    latest_speed: Mapped[float] = mapped_column(Float, nullable=True)
    latest_gps_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    route = relationship("Route", back_populates="vehicles")
    users = relationship("User", back_populates="vehicle")
    gps_records = relationship("GPSTracking", back_populates="vehicle", cascade="all, delete-orphan")
