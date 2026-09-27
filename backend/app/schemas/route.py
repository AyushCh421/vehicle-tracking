from pydantic import BaseModel, ConfigDict


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    route_number: str
    description: str | None = None


class RoutePointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latitude: float
    longitude: float
    sequence: int

    @staticmethod
    def from_model(point):
        return RoutePointResponse(
            latitude=point.latitude,
            longitude=point.longitude,
            sequence=point.sequence_number,
        )
