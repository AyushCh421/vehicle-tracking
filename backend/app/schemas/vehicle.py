from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_number: str
    registration_number: str
    vehicle_type: str
    status: str


class VehicleLocationResponse(BaseModel):
    vehicle_id: int
    latitude: float | None
    longitude: float | None
    speed: float | None
    status: str
    timestamp: datetime | None


class VehicleHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latitude: float
    longitude: float
    speed: float | None
    timestamp: datetime
