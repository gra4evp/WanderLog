WELCOME_MESSAGE = """
🌍 *Welcome to WanderLog!* 🌎

I'm your personal travel companion that brings adventures to life. Here's what I can do:

📍 *Live Location Tracking*
- Share your real-time movement
- Save favorite routes
- Get stats about your journeys

🗺 *Smart Features*
- Geofence alerts (e.g., "Near coffee shop")
- Photo location tagging
- Transport detection (walking/driving)

📊 *Weekly Reports*
- Distance covered
- Visited places
- Personal records

🔥 *Pro Tips*:
1. Use /trackme to start sharing location
2. Create zones with /geozone
3. Tag photos with #wanderlog

*Ready to explore?* Just share your location!

[ beta v0.9 | use /help anytime ]
"""

def get_error_message(error_type: str = "general") -> str:
    """
    Получение сообщения об ошибке

    Args:
    ----
        error_type: Тип ошибки

    Returns:
    -------
        Сообщение об ошибке

    """
    error_messages = {
        "file_too_large": "❌ Файл слишком большой. Максимальный размер: 10MB",
        "unsupported_format": "❌ Неподдерживаемый формат файла. Используйте JPG, JPEG, PNG или WEBP",
        "network_error": "❌ Ошибка сети. Проверьте подключение к интернету",
        "server_error": "❌ Ошибка сервера. Попробуйте позже",
        "timeout": "❌ Превышено время ожидания. Попробуйте еще раз",
        "general": "❌ Произошла ошибка. Попробуйте еще раз"
    }

    return error_messages.get(error_type, error_messages["general"])


def get_processing_message() -> str:
    """Получение сообщения о начале обработки"""
    return "🔄 Обрабатываю изображение..."


def get_success_message() -> str:
    """Получение сообщения об успешной обработке"""
    return "✅ Обработка завершена!"
