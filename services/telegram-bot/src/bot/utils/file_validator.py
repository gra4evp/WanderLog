from aiogram.types import Document
from config import Config


def validate_image_file(document: Document) -> bool:
    """
    Проверка, что документ является изображением
    
    Args:
        document: Документ для проверки
        
    Returns:
        True если файл является изображением
    """
    if not document.mime_type:
        return False
    
    # Проверяем MIME тип
    if not document.mime_type.startswith('image/'):
        return False
    
    # Проверяем расширение файла
    if document.file_name:
        file_extension = document.file_name.lower().split('.')[-1]
        if file_extension not in Config.SUPPORTED_FORMATS:
            return False
    
    # Проверяем размер файла
    if document.file_size and document.file_size > Config.MAX_FILE_SIZE:
        return False
    
    return True


def get_file_extension(filename: str) -> str:
    """
    Получение расширения файла
    
    Args:
        filename: Имя файла
        
    Returns:
        Расширение файла в нижнем регистре
    """
    return filename.lower().split('.')[-1] if '.' in filename else '' 