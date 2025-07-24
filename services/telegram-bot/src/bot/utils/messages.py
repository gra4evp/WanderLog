def get_welcome_message(user_name: str) -> str:
    """
    Получение приветственного сообщения

    Args:
    ----
        user_name: Имя пользователя

    Returns:
    -------
        Приветственное сообщение

    """
    return f"""
    👋 Привет, {user_name}!
    🏠 Я - бот для прогулок.
    📸 <b>Что я умею:</b>
    Нажмите кнопку ниже или отправьте изображение для начала работы!
    """.strip()


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
