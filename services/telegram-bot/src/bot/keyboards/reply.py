from config import CLASS_INFO
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
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
    """Клавиатура с кнопкой отмены"""
    keyboard = [
        [KeyboardButton(text="❌ Отмена")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_classes_info_keyboard() -> InlineKeyboardMarkup:
    """Инлайн клавиатура с информацией о классах"""
    keyboard = []
    for class_label, info in CLASS_INFO.items():
        button = InlineKeyboardButton(
            text=f"{info['emoji']} {class_label} [{info['description']}]",
            callback_data=f"class_label_{class_label}"
        )
        keyboard.append([button])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
