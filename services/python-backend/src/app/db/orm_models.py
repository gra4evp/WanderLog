# services/python-backend/src/app/db/orm_models.py
from datetime import datetime
from typing import ClassVar

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Index, UniqueConstraint, func, text

# JSON
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import (
    UUID,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    String,
)


class Base(DeclarativeBase):
    """Base class for all models"""

    # ================================== Table fields ===================================
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
    """User model for Telegram bot"""

    __tablename__: str = 'users'
    __table_args__: ClassVar[dict] = {'schema': 'geo'}

    # ================================== Table fields ===================================
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    language_code: Mapped[str] = mapped_column(String(8), nullable=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)

    # ================================== Relationships ==================================
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    track_points: Mapped[list["TrackPoint"]] = relationship(back_populates="user")

    def update(self, user_update: dict):
        """Update a user"""
        if 'username' in user_update:
            self.username = user_update['username']
        if 'first_name' in user_update:
            self.first_name = user_update['first_name']
        if 'last_name' in user_update:
            self.last_name = user_update['last_name']
        if 'language_code' in user_update:
            self.language_code = user_update['language_code']
        if 'is_bot' in user_update:
            self.is_bot = user_update['is_bot']

    # @classmethod
    # async def get_or_create(cls, session: AsyncSession, user_data: dict):
    #     """Get existing user or create new one"""
    #     user = await session.get(cls, user_data['id'])
    #     if not user:
    #         user = cls(
    #             id=user_data['id'],
    #             username=user_data.get('username'),
    #             first_name=user_data['first_name'],
    #             last_name=user_data.get('last_name'),
    #             language_code=user_data.get('language_code'),
    #             is_bot=user_data.get('is_bot', False)
    #         )
    #         session.add(user)
    #         await session.commit()
    #     return user


class TrackPoint(Base):
    """Track point model"""

    __tablename__: str = 'track_points'
    __table_args__: ClassVar[dict[str, str]] = {
        'schema': 'geo',
        'comment': 'GPS tracking points from user devices'
    }

    # ================================== Table fields ===================================
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default='now()'
    )
    location: Mapped[Geometry] = mapped_column(Geometry('POINT', srid=4326))  # WGS84
    accuracy: Mapped[float] = mapped_column(Float)  # В метрах
    elevation: Mapped[float] = mapped_column(Float, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSONB)  # Полные сырые данные с устройства
    session_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey('geo.sessions.id'),
        index=True
    )
    is_waypoint: Mapped[bool] = mapped_column(Boolean, default=False)  # Ручные точки маршрута
    note: Mapped[str] = mapped_column(String(200))  # Пользовательские заметки

    @classmethod
    async def is_hypertable(cls, engine: AsyncEngine) -> bool:
        """Checks if the table is a TimescaleDB hypertable"""
        schema_name = cls.__table_args__['schema']
        table_name = cls.__tablename__
        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM timescaledb_information.hypertables
                        WHERE hypertable_name = {table_name!r}
                        AND table_schema = {schema_name!r}
                    );
                    """
                )
            )
            return result.scalar()

    @classmethod
    async def create_hypertable(cls, engine: AsyncEngine):
        """Creates a hypertable for TrackPoint if it is not already created"""
        schema_name = cls.__table_args__['schema']
        table_name = cls.__tablename__
        if not await cls.is_hypertable(engine):
            async with engine.begin() as conn:
                await conn.execute(
                    text(
                        f"""
                        SELECT create_hypertable('{schema_name}.{table_name}', 'timestamp');
                        CREATE INDEX IF NOT EXISTS idx_user_time ON {schema_name}.{table_name} (user_id, timestamp DESC);
                        """
                    )
                )

    @classmethod
    async def enable_compression(
        cls,
        engine: AsyncEngine,
        segmentby: str = 'user_id',
        orderby: str = 'timestamp DESC'
    ):
        """Enables compression for the TrackPoint table"""
        schema_name = cls.__table_args__['schema']
        table_name = cls.__tablename__
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f"""
                    ALTER TABLE {schema_name}.{table_name} SET (
                        timescaledb.compress,
                        timescaledb.compress_orderby = '{orderby}',
                        timescaledb.compress_segmentby = '{segmentby}'
                    );
                    """
                )
            )

    @classmethod
    async def add_compression_policy(cls, engine: AsyncEngine, older_than: str = "30 days"):
        """Adds an automatic compression policy for TrackPoint"""
        schema_name = cls.__table_args__['schema']
        table_name = cls.__tablename__
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f"""
                    SELECT add_compression_policy(
                        '{schema_name}.{table_name}',
                        INTERVAL '{older_than}',
                        if_not_exists => true
                    );
                    """
                )
            )

    @classmethod
    async def add_retention_policy(cls, engine: AsyncEngine, older_than: str = "1 year"):
        """Adds a data retention policy for TrackPoint"""
        schema_name = cls.__table_args__['schema']
        table_name = cls.__tablename__
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f"""
                    SELECT add_retention_policy(
                        '{schema_name}.{table_name}',
                        INTERVAL '{older_than}',
                        if_not_exists => true
                    );
                    """
                )
            )


class GeoZone(Base):
    """Geo zone model"""

    __tablename__: str = 'geo_zones'
    __table_args__: ClassVar[dict[str, str]] = {'schema': 'geo'}

    # ================================== Table fields ===================================
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
            'comment': 'User activity sessions'
        }
    )

    # ================================== Table fields ===================================
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('geo.users.id'),
        index=True
    )
    session_token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='Unique session token for user session identification'
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    transport_type: Mapped[str] = mapped_column(
        ENUM('active', 'completed', 'paused', name='session_status_enum'),
        default='active'
    )

    # Statistics (calculated by triggers)
    total_distance: Mapped[float] = mapped_column(Float)  # в метрах
    points_count: Mapped[int] = mapped_column()
    bounds: Mapped[Geometry] = mapped_column(Geometry('POLYGON', srid=4326))  # Bounding box маршрута

    # ================================== Relationships ==================================
    user: Mapped["User"] = relationship(back_populates="sessions")

    def add_point(self, point: TrackPoint):
        """Updates session bounds when adding a point"""
        if not self.bounds:
            self.bounds = f'POLYGON(({point.lon} {point.lat}, ...))'
        else:
            self.bounds = func.ST_Expand(self.bounds, point)

    @classmethod
    async def is_hypertable(cls, engine: AsyncEngine) -> bool:
        """Checks if the table is a TimescaleDB hypertable"""
        schema_name = cls.__table_args__[-1]['schema']
        table_name = cls.__tablename__
        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM timescaledb_information.hypertables
                        WHERE hypertable_name = {table_name!r}
                        AND table_schema = {schema_name!r}
                    );
                    """
                )
            )
            return result.scalar()

    @classmethod
    async def create_hypertable(cls, engine: AsyncEngine):
        """Creates a hypertable for Session if it is not already created"""
        schema_name = cls.__table_args__[-1]['schema']
        table_name = cls.__tablename__
        if not await cls.is_hypertable(engine):
            async with engine.begin() as conn:
                await conn.execute(
                    text(
                        f"""
                        SELECT create_hypertable('{schema_name}.{table_name}', 'start_time');
                        CREATE INDEX IF NOT EXISTS idx_session_user_time ON {schema_name}.{table_name} (user_id, start_time DESC);
                        """
                    )
                )


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
            'comment': 'Saved user routes'
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
    simplified_path: Mapped[Geometry] = mapped_column(Geometry('LINESTRING', srid=4326))

    @classmethod
    async def is_hypertable(cls, engine: AsyncEngine) -> bool:
        """Checks if the table is a TimescaleDB hypertable"""
        schema_name = cls.__table_args__[-1]['schema']
        table_name = cls.__tablename__
        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM timescaledb_information.hypertables
                        WHERE hypertable_name = {table_name!r}
                        AND table_schema = {schema_name!r}
                    );
                    """
                )
            )
            return result.scalar()

    @classmethod
    async def create_hypertable(cls, engine: AsyncEngine):
        """Creates a hypertable for Route if it is not already created"""
        schema_name = cls.__table_args__[-1]['schema']
        table_name = cls.__tablename__
        if not await cls.is_hypertable(engine):
            async with engine.begin() as conn:
                await conn.execute(
                    text(
                        f"""
                        SELECT create_hypertable('{schema_name}.{table_name}', 'created_at');
                        CREATE INDEX IF NOT EXISTS idx_route_user_time ON {schema_name}.{table_name} (user_id, created_at DESC);
                        """
                    )
                )

    @classmethod
    async def enable_compression(cls, engine: AsyncEngine):
        """Enables compression for the Route table"""
        schema_name = cls.__table_args__[-1]['schema']
        table_name = cls.__tablename__
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f"""
                    ALTER TABLE {schema_name}.{table_name} SET (
                        timescaledb.compress,
                        timescaledb.compress_orderby = 'created_at DESC'
                    );
                    """
                )
            )

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
