import logging

from fastapi import APIRouter


logger = logging.getLogger(f"uvicorn.{__file__}")
router = APIRouter(prefix='/location')

@router.post('/tracks')
async def tracks():
    pass
