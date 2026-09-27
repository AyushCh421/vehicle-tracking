from pydantic import BaseModel, ConfigDict


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: str
    route_id: int
    vehicle_id: int
    is_active: bool
