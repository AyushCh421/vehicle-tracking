from sqlalchemy.orm import Session

from app.models.route import Route, RoutePoint
from app.models.user import User


def get_route_for_user(db: Session, user: User) -> Route | None:
    """
    Authorization boundary: a user may only ever see the route referenced
    by their own route_id. There is no route-by-arbitrary-id endpoint.
    """
    return db.query(Route).filter(Route.id == user.route_id).first()


def get_route_points_for_user(db: Session, user: User) -> list[RoutePoint]:
    return (
        db.query(RoutePoint)
        .filter(RoutePoint.route_id == user.route_id)
        .order_by(RoutePoint.sequence_number.asc())
        .all()
    )
