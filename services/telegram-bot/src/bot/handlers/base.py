import logging

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.reply import get_main_keyboard
from utils.messages import get_welcome_message


logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()

    welcome_text = get_welcome_message(message.from_user.first_name)
    keyboard = get_main_keyboard()

    await message.answer(
        welcome_text,
        reply_markup=keyboard
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
