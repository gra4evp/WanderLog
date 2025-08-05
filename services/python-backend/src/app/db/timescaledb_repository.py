import logging

from db.orm_models import GeoZone, Route, Session, TrackPoint, User
from schemas import TelegramUser, TelegramUserUpdate
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


# from sqlalchemy import select, delete, and_, text, func
# from sqlalchemy.orm import selectinload, joinedload


logger = logging.getLogger(f"uvicorn.{__file__}")


class UserNotFoundError(Exception):
    """Raised when a user is not found in the database."""

    pass


class TimescaleDBRepository:
    """Repository for TimescaleDB"""

    def __init__(self, db: AsyncSession):
        """Initialize the repository"""
        self.db = db

    async def create_user(self, user: TelegramUser) -> User:
        """Create a user"""
        new_user = User(**user.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user(self, user_id: int) -> User | None:
        """Get a user by their ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def update_user(self, user_id: int, user_update: TelegramUserUpdate) -> User:
        """Update a user"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError()
        user.update(user_update.model_dump())
        await self.db.commit()
        return user

    async def delete_user(self, user_id: int) -> None:
        """Delete a user"""
        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError()
        await self.db.delete(user)
        await self.db.commit()

    async def get_session(self, session_id: int) -> Session:
        """Get a session by its ID"""
        return await self.db.execute(select(Session).where(Session.id == session_id))

    async def get_track_point(self, track_point_id: int) -> TrackPoint:
        """Get a track point by its ID"""
        return await self.db.execute(select(TrackPoint).where(TrackPoint.id == track_point_id))

    async def get_geo_zone(self, geo_zone_id: int) -> GeoZone:
        """Get a geo zone by its ID"""
        return await self.db.execute(select(GeoZone).where(GeoZone.id == geo_zone_id))

    async def get_route(self, route_id: int) -> Route:
        """Get a route by its ID"""
        return await self.db.execute(select(Route).where(Route.id == route_id))

    async def get_all_users(self) -> list[User]:
        """Get all users"""
        return await self.db.execute(select(User))

    async def get_all_sessions(self) -> list[Session]:
        """Get all sessions"""
        return await self.db.execute(select(Session))
