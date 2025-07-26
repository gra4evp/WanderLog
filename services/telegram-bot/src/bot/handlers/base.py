import logging

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.reply import get_main_keyboard
from utils.messages import WELCOME_MESSAGE


logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()

    keyboard = get_main_keyboard()

    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

    logger.info(f"User {message.from_user.id} started the bot")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
    🤖 <b>Помощь по использованию бота</b>
    """
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего состояния"""
    await state.clear()
    keyboard = get_main_keyboard()

    await message.answer(
        "❌ Операция отменена. Выберите действие:",
        reply_markup=keyboard
    )


@router.message(F.text == "ℹ️ Помощь")
async def handle_help_button(message: Message):
    """Обработчик кнопки помощи"""
    await cmd_help(message)


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация базовых хендлеров"""
    dp.include_router(router)
