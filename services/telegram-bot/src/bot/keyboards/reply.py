from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота"""
    keyboard = [
        [
            KeyboardButton(text="📸 Start tracking"),
            KeyboardButton(text="ℹ️ Help")
        ],
        [
            KeyboardButton(text="❌ Cancel")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Choose action"
    )
