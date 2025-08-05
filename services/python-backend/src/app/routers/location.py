import logging

from fastapi import APIRouter


logger = logging.getLogger(f"uvicorn.{__file__}")
router = APIRouter(prefix='/location')

@router.post('/tracks')
async def tracks():
    pass

# Роуты
# @router.post("/users/start", status_code=201)
# async def start_tracking(
#     user_data: dict,
#     x_api_key: str = Depends(api_key_header),
#     repo: TimescaleDBRepository = Depends(get_repository)  # B008
# ):
#     """Register user and start tracking session"""
#     # В реальном приложении проверяем API-ключ бота
#     if x_api_key != "YOUR_BOT_API_KEY":
#         raise HTTPException(status_code=403, detail="Invalid API key")

#     try:
#         user = await repo.create_user(user_data)
#         new_session = Session(
#             user_id=user.id,
#             start_time=datetime.now(UTC),
#             session_token=str(uuid4())
#         )
#         db.add(new_session)
#         await db.commit()

#         return {
#             "session_id": str(new_session.id),
#             "message": "Tracking started"
#         }
#     except Exception as exc:
#         await db.rollback()
#         logger.error("Error", exc_info=exc)
#         raise HTTPException(status_code=400, detail=str(exc)) from exc
