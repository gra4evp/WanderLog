from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота"""
    keyboard = [
        [
            KeyboardButton(text="📸 Классифицировать изображение"),
            KeyboardButton(text="ℹ️ Помощь")
        ],
        [
            KeyboardButton(text="🏠 О классах интерьеров")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Отправьте изображение или выберите действие"
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard with cancel button"""
    keyboard = [
        [KeyboardButton(text="❌ Отмена")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
