from datetime import datetime

from pydantic import BaseModel


class TelegramUser(BaseModel):
    """Schema for creating a new user (registration)."""

    id: int  # Telegram user_id
    username: str | None = None
    first_name: str
    last_name: str | None = None
    language_code: str | None = None
    is_bot: bool = False


class TelegramUserUpdate(TelegramUser):
    """Schema for updating a user."""

    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    is_bot: bool | None = None


class UserCreateRequest(BaseModel):
    """Schema for creating a new user (registration)."""

    user: TelegramUser
    metadata: dict | None = None


class UserCreateResponse(BaseModel):
    """Schema for creating a new user (registration)."""

    user: TelegramUser
    created: bool


class UserGetResponse(BaseModel):
    """Schema for reading a user."""

    user: TelegramUser


class UserUpdateRequest(BaseModel):
    """Schema for updating a user."""

    user_update: TelegramUserUpdate
    metadata: dict | None = None


class UserUpdateResponse(BaseModel):
    """Schema for updating a user."""

    user: TelegramUser
    updated: bool


class Location(BaseModel):
    """Schema for receiving a location point."""

    date_time: datetime
    latitude: float
    longitude: float
    accuracy: float
    elevation: float | None = None
    note: str | None = None
    is_waypoint: bool = False


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
