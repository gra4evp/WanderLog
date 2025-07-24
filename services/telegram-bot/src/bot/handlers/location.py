import logging

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove


router = Router()
logger = logging.Logger("LOCATION")

router = Router()
logger = logging.getLogger("LOCATION")

# Включаем логирование в консоль
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@router.message(Command("track_me"))
async def start_tracking(message: Message):
    """Запуск трансляции местоположения"""
    await message.answer(
        "📍 Нажмите кнопку ниже, чтобы начать трансляцию ваших координат.\n"
        "Я буду логировать их в реальном времени.\n\n"
        "Чтобы остановить - отправьте /stop_live",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[
                KeyboardButton(
                    text="📍 Начать трансляцию",
                    request_location=True
                )
            ]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@router.message(F.location)
async def handle_initial_location(message: Message):
    """Обработка первого запроса на трансляцию"""
    await message.answer(
        "Трансляция координат начата!",
        reply_markup=ReplyKeyboardRemove()
    )
    await log_location(message)


@router.edited_message(F.location)
async def handle_live_update(message: Message):
    """Обработка обновлений live-локации"""
    await log_location(message)


async def log_location(message: Message):
    """Логирование координат"""
    loc = message.location
    logger.info(
        "Получены координаты: lat=%.6f, lon=%.6f, accuracy=%s, live=%s",
        loc.latitude,
        loc.longitude,
        loc.horizontal_accuracy or "N/A",
        "Live" if hasattr(message, 'edit_date') else "Static"
    )


@router.message(Command("stop_live"))
async def stop_tracking(message: Message):
    """Остановка трансляции"""
    await message.answer(
        "Трансляция координат остановлена",
        reply_markup=ReplyKeyboardRemove()
    )
    logger.info("Пользователь %d остановил трансляцию", message.from_user.id)


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация базовых хендлеров"""
    dp.include_router(router)
