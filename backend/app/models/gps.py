from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GPSTracking(Base):
    __tablename__ = "gps_tracking"
    __table_args__ = (
        Index("ix_gps_vehicle_timestamp", "vehicle_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    speed: Mapped[float] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    vehicle = relationship("Vehicle", back_populates="gps_records")
