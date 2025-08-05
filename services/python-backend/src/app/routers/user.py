import logging

from db.database import get_repository
from db.timescaledb_repository import TimescaleDBRepository, UserNotFoundError
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import UserCreateRequest, UserCreateResponse, UserGetResponse, UserUpdateRequest, UserUpdateResponse


# Geometry point as WKT
# from geoalchemy2.shape import from_shape
#from shapely.geometry import Point


logger = logging.getLogger(f"uvicorn.{__file__}")
router = APIRouter(prefix='/users')


# api_key_header = APIKeyHeader(name="X-API-Key")


@router.post(
    '/',
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=['user'],
    summary="Create new user (registration). If user already exists, returns existing user."
)
async def create_user(
    request: UserCreateRequest,
    repo: TimescaleDBRepository = Depends(get_repository)  # noqa B008
):
    """Create new user (registration). If user already exists, returns existing user."""
    try:
        existing_user = await repo.get_user(request.user.id)
        if existing_user is not None:
            return UserCreateResponse(user=existing_user, created=False)
        new_user = await repo.create_user(request.user)
        return UserCreateResponse(user=new_user, created=True)
    except Exception as exc:
        logger.error(f"Error creating user: {exc}", exc_info=exc)
        repo.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc


@router.get(
    '/{user_id}',
    response_model=UserGetResponse,
    tags=['user'],
    summary="Get user by ID"
)
async def get_user(
    user_id: int,
    repo: TimescaleDBRepository = Depends(get_repository)  # noqa B008
):
    """Get user information by ID. If user not found, returns 404 error."""
    try:
        user = await repo.get_user(user_id)
        if user is None:
            raise UserNotFoundError()
        return UserGetResponse(user=user)
    except Exception as exc:
        logger.error(f"Error getting user: {exc}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc


@router.put(
    '/{user_id}',
    response_model=UserUpdateResponse,
    tags=['user'],
    summary="Fully update user"
)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    repo: TimescaleDBRepository = Depends(get_repository)  # noqa B008
):
    """Fully update user information."""
    try:
        updated_user = await repo.update_user(user_id, request.user_update)
    except UserNotFoundError as exc:
        logger.error(f"User not found: {exc}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        ) from exc
    except Exception as exc:
        logger.error(f"Error updating user: {exc}", exc_info=exc)
        repo.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc
    return UserUpdateResponse(user=updated_user, updated=True)


@router.delete(
    '/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['user'],
    summary="Delete user"
)
async def delete_user(
    user_id: int,
    repo: TimescaleDBRepository = Depends(get_repository)  # noqa B008
):
    """Delete user by ID."""
    try:
        await repo.delete_user(user_id)
    except UserNotFoundError as exc:
        logger.error(f"User not found: {exc}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        ) from exc
    except Exception as exc:
        logger.error(f"Error deleting user: {exc}", exc_info=exc)
        repo.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc


# @router.post(
#     '/location',
#     response_model=LocationRead,
#     status_code=status.HTTP_201_CREATED,
#     tags=['user']
# )
# async def send_location(
#     loc: LocationCreate,
#     db: AsyncSession = Depends(get_db)  # B008
# ):
#     point = from_shape(Point(loc.longitude, loc.latitude), srid=4326)
#     new_point = TrackPoint(
#         user_id=loc.user_id,
#         timestamp=datetime.now(UTC),
#         location=point,
#         accuracy=loc.accuracy,
#         elevation=loc.elevation,
#         note=loc.note,
#         is_waypoint=loc.is_waypoint,
#         raw_data=loc.raw_data or {},
#         session_id=loc.session_id
#     )
#     db.add(new_point)
#     await db.commit()
#     await db.refresh(new_point)
#     # Extract lat/lon for response
#     coords = new_point.location.coords[0] if hasattr(new_point.location, 'coords') else (loc.longitude, loc.latitude)
#     return LocationRead(
#         id=new_point.id,
#         user_id=new_point.user_id,
#         timestamp=new_point.timestamp.isoformat(),
#         latitude=coords[1],
#         longitude=coords[0],
#         accuracy=new_point.accuracy,
#         elevation=new_point.elevation,
#         note=new_point.note,
#         is_waypoint=new_point.is_waypoint,
#         session_id=str(new_point.session_id) if new_point.session_id else None,
#         raw_data=new_point.raw_data
#     )
