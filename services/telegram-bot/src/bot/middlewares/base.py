import logging
import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования запросов"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Логируем входящие сообщения
        if isinstance(event, Message):
            user_id = event.from_user.id
            username = event.from_user.username or "Unknown"
            text = event.text or "No text"
            
            logging.info(f"Message from {username}({user_id}): {text}")
            
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            username = event.from_user.username or "Unknown"
            callback_data = event.data or "No data"
            
            logging.info(f"Callback from {username}({user_id}): {callback_data}")
        
        # Засекаем время выполнения
        start_time = time.time()
        
        try:
            result = await handler(event, data)
            execution_time = time.time() - start_time
            logging.info(f"Handler executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"Handler error after {execution_time:.2f}s: {e}")
            raise


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware to limit the frequency of user requests (anti-flood).
    - For single messages: applies throttling per user.
    - For media groups (albums): throttling is applied only to the first message of the group; all messages in the group are allowed without delay.
    """
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.last_request = {}
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()

        # If this is part of a media group (album), apply throttling only to the first message in the group.
        if isinstance(event, Message) and event.media_group_id is not None:
            group_key = f"{user_id}:{event.media_group_id}"
            if group_key not in self.last_request:
                self.last_request[group_key] = current_time
            # Allow all messages in the group without additional throttling
            return await handler(event, data)

        # Standard throttling for single (non-group) messages
        if user_id in self.last_request:
            time_passed = current_time - self.last_request[user_id]
            if time_passed < self.rate_limit:
                await event.answer("⚠️ Слишком много запросов. Подождите немного.")
                return
        
        self.last_request[user_id] = current_time
        return await handler(event, data)


def setup_middlewares(dp):
    """Настройка всех middleware"""
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware()) 