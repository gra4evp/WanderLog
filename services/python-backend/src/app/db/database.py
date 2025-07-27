# services/python-backend/src/app/db/database.py
import os
from collections.abc import AsyncGenerator

from db.orm_models import Base
from db.timescaledb_repository import TimescaleDBRepository
from fastapi import Depends
from sqlalchemy import text  # Для выполнения сырых SQL-запросов
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://admin:password@timescaledb:5432/mydb')

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)

async def create_tables():
    engine.echo = True
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаём таблицы, если они ещё не существуют

        #  ======================= Выполняем SQL-запросы для TimescaleDB ==========================
        # 1. Преобразование в гипертейбл
        # Проверяем, является ли таблица thermal_data гипертаблицей
        result = await conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM timescaledb_information.hypertables
                    WHERE hypertable_name = 'thermal_data'
                );
                """
            )
        )
        is_hypertable = result.scalar()

        # Если таблица не является гипертаблицей, преобразуем её
        if not is_hypertable:
            await conn.execute(
                text(
                    """
                    SELECT create_hypertable('thermal_data', by_range('timestamp', INTERVAL '1 day'));
                    """
                )
            )

        # 2. Включение компрессии, здесь подготавливается таблица для работы с компрессией
        await conn.execute(
            text(
                """
                ALTER TABLE thermal_data SET (
                    timescaledb.compress,
                    timescaledb.compress_orderby = 'timestamp DESC',
                    timescaledb.compress_segmentby = 'zone_id'
                );
                """
            )
        )

        # 3. Добавление политики компрессии, автоматическое сжатие для данных старше 30 дней
        await conn.execute(text("""SELECT add_compression_policy('thermal_data', INTERVAL '30 days', if_not_exists => true);"""))

        # 4. Добавляем политику хранения данных (если она ещё не существует)
        await conn.execute(
            text(
                """
                SELECT add_retention_policy('thermal_data', INTERVAL '1 year', if_not_exists => true);
                """
            )
        )

    engine.echo = False


async def drop_tables():
    """Function only for testing"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session_factory() -> async_sessionmaker:
    return async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронный генератор для управления сессией базы данных.

    Создаёт сессию для работы с базой данных, передаёт её обработчику запроса,
    а затем автоматически закрывает после завершения запроса.

    Возвращает:
        AsyncGenerator[AsyncSession, None]: Асинхронный генератор, который отдаёт сессию
        и завершает её после использования.
    """
    async with async_session_factory() as session:  # Открываем сессию с БД
        yield session  # Передаём сессию обработчику запроса
    # После выхода из `yield`, блок `async with` автоматически закроет сессию


async def get_repository(
    db: AsyncSession = Depends(get_db)  # noqa B008
) -> TimescaleDBRepository:
    """Зависимость для получения репозитория с сессией базы данных"""
    return TimescaleDBRepository(db)
