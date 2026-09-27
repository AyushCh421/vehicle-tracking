from datetime import datetime

from pydantic import BaseModel, field_validator


class GPSMessage(BaseModel):
    """Shape of the JSON payload published to vehicles/{vehicle_id}/gps"""
    latitude: float
    longitude: float
    speed: float | None = None
    timestamp: datetime | None = None

    @field_validator("latitude")
    @classmethod
    def valid_lat(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError("latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def valid_lon(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return v
