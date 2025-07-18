import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Конфигурация бота"""
    
    # Токен бота (получить у @BotFather)
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # URL бэкенда для классификации
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Таймаут для запросов к API (в секундах)
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Максимальный размер файла (в байтах) - 10MB
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))
    
    # Поддерживаемые форматы изображений
    SUPPORTED_FORMATS: tuple = ("jpg", "jpeg", "png", "webp")
    
    # Количество изображений в одном запросе
    MAX_IMAGES_PER_REQUEST: int = int(os.getenv("MAX_IMAGES_PER_REQUEST", "5"))
    
    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate(cls) -> bool:
        """Проверка корректности конфигурации"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен")
        
        if not cls.BACKEND_URL:
            raise ValueError("BACKEND_URL не установлен")
        
        return True 

# Глобальный объект с информацией о классах интерьера
# norm
# CLASS_INFO = {
#     'A0': {'emoji': '🧱', 'description': 'Unfinished | Без отделки'},
#     'A1': {'emoji': '◻️', 'description': 'WhiteBox | Под чистовую'},
#     'B0': {'emoji': '🏚️', 'description': 'Major repair | Капитальный ремонт'},
#     'B1': {'emoji': '🎨', 'description': 'Cosmetic repair | Косметический ремонт'},
#     'C0': {'emoji': '☑️', 'description': 'Finished | Чистовая'},
#     'C1': {'emoji': '🏠', 'description': 'Good | Хорошее состояние'},
#     'D0': {'emoji': '✨', 'description': 'Euro-style | Евроремонт'},
#     'D1': {'emoji': '💎', 'description': 'Luxury | Люкс'},
# }

# сringe (customer requires)
CLASS_INFO = {
    'A0': {'emoji': '🧱', 'description': 'Без отделки'},
    'A1': {'emoji': '◻️', 'description': 'White box (под чистовую отделку)'},
    'B0': {'emoji': '🏚️', 'description': 'Эконом (бабушкин ремонт)'},
    'B1': {'emoji': '🎨', 'description': 'Эконом+ (дешёвый ремонт в новостройках)'},
    'C0': {'emoji': '☑️', 'description': 'Стандарт (нормальный средний класс)'},
    'C1': {'emoji': '🏠', 'description': 'Стандарт+ (хороший обычный ремонт)'},
    'D0': {'emoji': '✨', 'description': 'Евроремонт'},
    'D1': {'emoji': '💎', 'description': 'Luxe (дизайнерский)'}
}
