"""Routers package initialization."""

__all__ = [
    "location_router",
    "user_router"
]

from .location import router as location_router
from .user import router as user_router
