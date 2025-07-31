from pydantic import BaseModel


class UserCreate(BaseModel):
    """Schema for creating a new user (registration)."""

    id: int  # Telegram user_id
    username: str | None = None
    first_name: str
    last_name: str | None = None
    language_code: str | None = None
    is_bot: bool = False

class UserRead(BaseModel):
    """Schema for reading user information."""

    id: int
    username: str | None = None
    first_name: str
    last_name: str | None = None
    language_code: str | None = None
    is_bot: bool

    class Config:
        """Pydantic config for ORM mode."""

        orm_mode = True

class LocationCreate(BaseModel):
    """Schema for submitting a new location point."""

    user_id: int
    latitude: float
    longitude: float
    accuracy: float
    elevation: float | None = None
    note: str | None = None
    is_waypoint: bool = False
    raw_data: dict | None = None
    session_id: str | None = None

class LocationRead(BaseModel):
    """Schema for reading a location point."""

    id: int
    user_id: int
    timestamp: str
    latitude: float
    longitude: float
    accuracy: float
    elevation: float | None = None
    note: str | None = None
    is_waypoint: bool
    session_id: str | None = None
    raw_data: dict | None = None

    class Config:
        """Pydantic config for ORM mode."""

        orm_mode = True
