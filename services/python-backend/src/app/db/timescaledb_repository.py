import logging

from db.orm_models import GeoZone, Route, Session, TrackPoint, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# from sqlalchemy import select, delete, and_, text, func
# from sqlalchemy.orm import selectinload, joinedload


logger = logging.getLogger(f"uvicorn.{__file__}")


class TimescaleDBRepository:
    """Repository for TimescaleDB"""

    def __init__(self, db: AsyncSession):
        """Initialize the repository"""
        self.db = db

    async def get_user(self, user_id: int) -> User:
        """Get a user by their ID"""
        return await self.db.execute(select(User).where(User.id == user_id))

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
