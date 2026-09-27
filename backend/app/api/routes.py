from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.route import RouteResponse, RoutePointResponse
from app.services.auth_service import get_current_user
from app.services.route_service import get_route_for_user, get_route_points_for_user

router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("/me", response_model=RouteResponse)
def get_my_route(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    route = get_route_for_user(db, current_user)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return route


@router.get("/me/points", response_model=list[RoutePointResponse])
def get_my_route_points(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    points = get_route_points_for_user(db, current_user)
    return [RoutePointResponse.from_model(p) for p in points]
