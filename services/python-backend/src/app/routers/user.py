import logging
from datetime import UTC, datetime
from uuid import uuid4

from db.database import get_db
from db.orm_models import Session, TrackPoint, User
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic_models import LocationCreate, LocationRead, UserCreate, UserRead
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(f"uvicorn.{__file__}")
router = APIRouter(prefix='/users')


api_key_header = APIKeyHeader(name="X-API-Key")


# Роуты
@router.post("/users/start", status_code=201)
async def start_tracking(
    user_data: dict,
    x_api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db)  # noqa B008
):
    """Register user and start tracking session"""
    # В реальном приложении проверяем API-ключ бота
    if x_api_key != "YOUR_BOT_API_KEY":
        raise HTTPException(status_code=403, detail="Invalid API key")

    try:
        user = await User.get_or_create(db, user_data)
        new_session = Session(
            user_id=user.id,
            start_time=datetime.now(UTC),
            session_token=str(uuid4())
        )
        db.add(new_session)
        await db.commit()

        return {
            "session_id": str(new_session.id),
            "message": "Tracking started"
        }
    except Exception as exc:
        await db.rollback()
        logger.error("Error", exc_info=exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)  # noqa B008
):
    existing = await db.get(User, user.id)
    if existing:
        return existing
    new_user = User(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
        is_bot=user.is_bot
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post('/location', response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def send_location(
    loc: LocationCreate,
    db: AsyncSession = Depends(get_db)  # noqa B008
):
    # Geometry point as WKT
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point
    point = from_shape(Point(loc.longitude, loc.latitude), srid=4326)
    new_point = TrackPoint(
        user_id=loc.user_id,
        timestamp=datetime.now(UTC),
        location=point,
        accuracy=loc.accuracy,
        elevation=loc.elevation,
        note=loc.note,
        is_waypoint=loc.is_waypoint,
        raw_data=loc.raw_data or {},
        session_id=loc.session_id
    )
    db.add(new_point)
    await db.commit()
    await db.refresh(new_point)
    # Extract lat/lon for response
    coords = new_point.location.coords[0] if hasattr(new_point.location, 'coords') else (loc.longitude, loc.latitude)
    return LocationRead(
        id=new_point.id,
        user_id=new_point.user_id,
        timestamp=new_point.timestamp.isoformat(),
        latitude=coords[1],
        longitude=coords[0],
        accuracy=new_point.accuracy,
        elevation=new_point.elevation,
        note=new_point.note,
        is_waypoint=new_point.is_waypoint,
        session_id=str(new_point.session_id) if new_point.session_id else None,
        raw_data=new_point.raw_data
    )
