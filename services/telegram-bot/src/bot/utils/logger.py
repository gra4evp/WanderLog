import logging
import sys
from config import Config


def setup_logger():
    """Настройка логирования для бота"""
    
    # Создаем форматтер
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Очищаем существующие хендлеры
    root_logger.handlers.clear()
    
    # Создаем хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Создаем хендлер для файла (опционально)
    try:
        file_handler = logging.FileHandler('bot.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")
    
    # Устанавливаем уровень для сторонних библиотек
    logging.getLogger('aiogram').setLevel(logging.INFO)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    logging.info("Logger setup completed") 