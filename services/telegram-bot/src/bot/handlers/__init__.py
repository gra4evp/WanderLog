"""Handlers package for registering all bot handlers."""

from aiogram import Dispatcher

from .base import register_handlers as register_base_handlers
from .location import register_handlers as register_location_handlers


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация всех хендлеров"""
    register_base_handlers(dp)
    register_location_handlers(dp)
