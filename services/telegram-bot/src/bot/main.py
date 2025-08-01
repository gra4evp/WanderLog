import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers import register_handlers
from middlewares.base import setup_middlewares
from utils.logger import setup_logger


# Настройка логирования
setup_logger()
logger = logging.getLogger(__name__)


async def main():
    """The main function of launching the bot."""
    logger.info("Starting bot...")

    config = Config()
    # Проверяем конфигурацию
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    # Инициализация бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Используем MemoryStorage для состояний
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Настройка middleware
    setup_middlewares(dp)

    # Регистрация всех хендлеров
    register_handlers(dp)

    try:
        logger.info("Bot started successfully!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
