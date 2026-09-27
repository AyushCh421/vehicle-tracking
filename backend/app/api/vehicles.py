from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.vehicle import VehicleResponse, VehicleLocationResponse, VehicleHistoryItem
from app.services.auth_service import get_current_user
from app.services.vehicle_service import get_vehicle_for_user, get_history_for_user

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("/me", response_model=VehicleResponse)
def get_my_vehicle(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vehicle = get_vehicle_for_user(db, current_user)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


@router.get("/me/location", response_model=VehicleLocationResponse)
def get_my_vehicle_location(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vehicle = get_vehicle_for_user(db, current_user)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    if vehicle.latest_gps_timestamp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle location unavailable")

    return VehicleLocationResponse(
        vehicle_id=vehicle.id,
        latitude=vehicle.latest_latitude,
        longitude=vehicle.latest_longitude,
        speed=vehicle.latest_speed,
        status=vehicle.status,
        timestamp=vehicle.latest_gps_timestamp,
    )


@router.get("/me/history", response_model=list[VehicleHistoryItem])
def get_my_vehicle_history(
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = get_history_for_user(db, current_user, limit=limit, from_ts=from_, to_ts=to)
    return records
