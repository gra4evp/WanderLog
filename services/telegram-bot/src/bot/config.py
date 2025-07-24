import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """Конфигурация бота."""

    BOT_TOKEN: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))  # Bot token (get from @BotFather)

    # URL бэкенда для классификации
    BACKEND_URL: str = field(default_factory=lambda: os.getenv("BACKEND_URL", "http://localhost:8000"))

    # Таймаут для запросов к API (в секундах)
    API_TIMEOUT: int = field(default_factory=lambda: int(os.getenv("API_TIMEOUT", "30")))

    # Максимальный размер файла (в байтах) - 10MB
    MAX_FILE_SIZE: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", "10485760")))

    # Поддерживаемые форматы изображений
    SUPPORTED_FORMATS: tuple = ("jpg", "jpeg", "png", "webp")

    # Количество изображений в одном запросе
    MAX_IMAGES_PER_REQUEST: int = field(default_factory=lambda: int(os.getenv("MAX_IMAGES_PER_REQUEST", "5")))

    # Настройки логирования
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def validate(self) -> bool:
        """Проверка корректности конфигурации"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен")
        if not self.BACKEND_URL:
            raise ValueError("BACKEND_URL не установлен")
        return True
