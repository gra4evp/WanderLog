# services/python-backend/src/app/db/orm_models.py
from datetime import datetime
from typing import ClassVar

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Index, UniqueConstraint, func, text

# JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import (
    UUID,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    String,
)


class Base(DeclarativeBase):
    """Base class for all models"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


class User(Base):
    """User model"""

    __tablename__: str = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    username: Mapped[str] = mapped_column(String(64))
    settings: Mapped[dict] = mapped_column(JSONB)  # {units: 'metric', privacy: 'friends_only'}


class TrackPoint(Base):
    """Track point model"""

    __tablename__: str = 'track_points'
    __table_args__: ClassVar[dict[str, str]] = {
        'schema': 'geo',
        'postgresql_using': {
            'timescaledb.compress': 'true',
            'timescaledb.compress_segmentby': 'user_id',
            'timescaledb.compress_orderby': 'timestamp'
        }
    }

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default='now()')
    location: Mapped[Geometry] = mapped_column(Geometry('POINT', srid=4326))  # WGS84
    accuracy: Mapped[float] = mapped_column(Float)  # В метрах
    elevation: Mapped[float] = mapped_column(Float, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSONB)  # Полные сырые данные с устройства
    session_id: Mapped[int] = mapped_column(UUID, ForeignKey('geo.sessions.id'), index=True)
    is_waypoint: Mapped[bool] = mapped_column(Boolean, default=False)  # Ручные точки маршрута
    note: Mapped[str] = mapped_column(String(200))  # Пользовательские заметки

    @classmethod
    async def create_hypertable(cls, engine: AsyncEngine):
        """Create a hypertable for the track points"""
        async with engine.begin() as conn:  # begin() автоматически коммитит
            await conn.execute(
                text(
                    f"SELECT create_hypertable('geo.{cls.__tablename__}', 'timestamp');"
                    "CREATE INDEX idx_user_time ON geo.track_points (user_id, timestamp DESC);"
                )
            )


class GeoZone(Base):
    """Geo zone model"""

    __tablename__: str = 'geo_zones'
    __table_args__: ClassVar[dict[str, str]] = {'schema': 'geo'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(100))
    zone_type: Mapped[str] = mapped_column(String(30))  # home/work/favorite/custom
    geometry: Mapped[Geometry] = mapped_column(Geometry('POLYGON', srid=4326))
    notify_on_enter: Mapped[bool] = mapped_column(Boolean, default=True)
    radius: Mapped[float] = mapped_column(Float)  # Для окружностей

    @hybrid_property
    def area_sq_meters(self):
        """Area as meters"""
        return func.ST_Area(
            func.ST_Transform(self.geometry, 3857)  # Web Mercator для метров
        )


class Session(Base):
    """Session model"""

    __tablename__: str = 'sessions'
    __table_args__: ClassVar[tuple[..., dict[str, str]]] = (
        # Positional arguments (constraints):
        Index('idx_session_user', 'user_id', 'start_time'),
        UniqueConstraint(
            'user_id',
            'session_token',
            name='uq_user_session'
        ),

        # Keyword arguments (table settings), must be last:
        {
            'schema': 'geo',
            'comment': 'Сессии активности пользователей',
            'postgresql_using': 'timescaledb'
        }
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    transport_type: Mapped[str] = mapped_column(Enum('active', 'completed', 'paused'), default='active')

    # Statistics (calculated by triggers)
    total_distance: Mapped[float] = mapped_column(Float)  # в метрах
    points_count: Mapped[int] = mapped_column()
    bounds: Mapped[Geometry] = mapped_column(Geometry('POLYGON', srid=4326))  # Bounding box маршрута

    # Методы
    def add_point(self, point: TrackPoint):
        """Обновляет границы сессии при добавлении точки"""
        if not self.bounds:
            self.bounds = f'POLYGON(({point.lon} {point.lat}, ...))'
        else:
            self.bounds = func.ST_Expand(self.bounds, point)


class Route(Base):
    """Route model"""

    __tablename__: str = 'routes'
    __table_args__ = (
        # ========================= Positional arguments (constraints) ============================
        # Indexes
        Index('idx_route_path', 'path', postgresql_using='gist'),

        # =================== Keyword arguments (table settings), must be last ====================
        {
            'schema': 'geo',
            'comment': 'Сохраненные маршруты',
            'postgresql_with': {
                'timescaledb.compress': 'true',
                'timescaledb.compress_orderby': 'created_at'
            }
        }
    )

    id: Mapped[int] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    session_id: Mapped[int] = mapped_column(UUID, ForeignKey('geo.sessions.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    tags: Mapped[dict] = mapped_column(JSONB)  # {'scenic': True, 'public': False}

    # Геометрия (линия из всех точек)
    path: Mapped[Geometry] = mapped_column(Geometry('LINESTRING', srid=4326))
    simplified_path: Mapped[Geometry] = mapped_column(Geometry('LINESTRING', srid=4326))  # Упрощенная версия

    # Триггер для автоматического построения маршрута
    @staticmethod
    def create_route_trigger():
        """Create route trigger for updating path and simplified_path"""
        return text(
        """
        CREATE OR REPLACE FUNCTION update_route_path()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.path = (
                SELECT ST_MakeLine(location ORDER BY timestamp)
                FROM geo.track_points
                WHERE session_id = NEW.session_id
            );
            NEW.simplified_path = ST_Simplify(NEW.path, 0.0001);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER route_path_update
        BEFORE INSERT OR UPDATE ON geo.routes
        FOR EACH ROW EXECUTE FUNCTION update_route_path();
        """
    )
