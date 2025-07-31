# services/python-backend/src/app/db/database.py
import os
from collections.abc import AsyncGenerator

from db.orm_models import Base, TrackPoint
from db.timescaledb_repository import TimescaleDBRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql+asyncpg://admin:password@timescaledb:5432/mydb'
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)

async def create_tables():
    engine.echo = True
    async with engine.begin() as conn:
        # Creating tables if they don't exist yet
        await conn.run_sync(Base.metadata.create_all)

    #  ==================== Executing SQL queries for TimescaleDB =======================
    # 1. Converting the "track_points" table into a hypertable
    TrackPoint.create_hypertable(engine=engine)

    #2. Enabling compression, the table is being prepared to work with compression
    TrackPoint.enable_compression(engine=engine)

    #3. Adding compression policy, automatic compression for data older than 30 days
    TrackPoint.add_compression_policy(engine=engine, older_than="30 days")

    #4. Adding a data retention policy (if it doesn't already exist)
    TrackPoint.add_retention_policy(engine=engine)

    engine.echo = False


async def drop_tables():
    """Function only for testing"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session_factory() -> async_sessionmaker:
    return async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous generator for managing the database session.

    Creates a session for working with the database, passes it to the request handler,
    and then automatically closes it after the request is completed.

    Returns
    -------
        AsyncGenerator[AsyncSession, None]: An asynchronous generator that yields the session
        and closes it after use.

    """
    async with async_session_factory() as session:  # Open a session with the DB
        yield session  # Pass the session to the request handler
    # After exiting `yield`, the `async with` block will automatically close the session


async def get_repository(
    db: AsyncSession = Depends(get_db)  # noqa B008
) -> TimescaleDBRepository:
    """Dependency for obtaining a repository with a database session"""
    return TimescaleDBRepository(db)
