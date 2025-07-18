import logging
from aiogram import Dispatcher, Router, F
from aiogram.types import Message, PhotoSize, Document
from aiogram.filters import Command
from io import BytesIO
import uuid

from services.classification_service import ClassificationService
from utils.file_validator import validate_image_file
from utils.response_formatter import format_classification_result
from keyboards.reply import get_main_keyboard
from config import Config
from middlewares.album import AlbumMiddleware

logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(AlbumMiddleware())


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.message(Command("classify"))
async def cmd_classify(message: Message):
    """Команда для начала классификации"""
    await message.answer(
        "📸 Отправьте изображение интерьера для классификации.\n\n"
        "Поддерживаемые форматы: JPG, JPEG, PNG, WEBP\n"
        "Максимальный размер: 10MB\n"
        "Можно отправить до 5 изображений одновременно."
    )


def is_supported(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)


async def extract_file_and_name(
        message: Message,
        image_filename: str = None
    ) -> tuple[BytesIO, str] | None:
    """
    Extracts file and filename from a message if it's a supported image.
    For photos, uses image_filename if provided. For documents, always uses the original filename
    """
    if message.photo:
        file = message.photo[-1]
        filename = image_filename or f"photo_{file.file_id[:4]}.jpg"
    elif message.document and is_supported(message.document.file_name):
        file = message.document
        filename = message.document.file_name  # Always use original name for documents
    else:
        return None
    
    file_info = await message.bot.get_file(file.file_id)
    file_data = await message.bot.download_file(file_info.file_path)
    file_bytes = file_data.read()
    return BytesIO(file_bytes), filename


async def process_images(files: list[tuple[BytesIO, str]]) -> dict:
    """
    Классифицирует изображения и возвращает результат.
    """
    classification_service = ClassificationService()
    return await classification_service.classify_multiple_images(files)


@router.message(F.photo | F.document)
async def handle_images(message: Message, album: list[Message] = None):
    """
    Universal handler for single and batch images.
    If album is not None, it's a batch; otherwise, it's a single image.
    """
    files = []
    messages = []
    processing_message = await message.answer("🔄 Обрабатываю изображение(я)...")
    if album:
        # Batch of images (album)
        for idx, msg in enumerate(album, start=1):
            result = await extract_file_and_name(msg, image_filename=f"image_{idx}.jpg")
            if result:
                files.append(result)
                messages.append(msg)
        if not files:
            await message.answer("❌ Не удалось найти подходящие изображения в альбоме.")
            return
    else:
        # Single image
        result = await extract_file_and_name(message, image_filename="image.jpg")
        if not result:
            await message.answer("❌ Неподдерживаемый формат файла. Поддерживаются JPG, JPEG, PNG, WEBP.")
            return
        files.append(result)
        messages.append(message)

    try:
        response = await process_images(files)
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        await message.answer("❌ Произошла ошибка при классификации. Попробуйте позже.")
        return

    await processing_message.delete()

    # Для каждого результата делаем reply на соответствующее сообщение
    for res, msg in zip(response.get("results", []), messages):
        formatted_text = format_classification_result(res)
        await msg.reply(formatted_text, parse_mode="HTML")


def register_image_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров для работы с изображениями"""
    dp.include_router(router)
