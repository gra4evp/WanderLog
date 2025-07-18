from aiogram import Dispatcher
from .base import register_base_handlers
from .image_classification import register_image_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    """Регистрация всех хендлеров"""
    register_base_handlers(dp)
    register_image_handlers(dp) 