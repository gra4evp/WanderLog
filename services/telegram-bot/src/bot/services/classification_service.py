import logging
import aiohttp
import asyncio
from typing import List, Dict, Any
from io import BytesIO

from config import Config

logger = logging.getLogger(__name__)


class ClassificationService:
    """Сервис для работы с API классификации"""
    
    def __init__(self):
        self.base_url = Config.BACKEND_URL
        self.timeout = aiohttp.ClientTimeout(total=Config.API_TIMEOUT)
    
    async def classify_single_image(self, file_data: BytesIO, filename: str) -> Dict[str, Any]:
        """
        Классификация одного изображения
        
        Args:
            file_data: Данные файла
            filename: Имя файла
            
        Returns:
            Результат классификации
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Подготавливаем данные для отправки
                data = aiohttp.FormData()
                data.add_field(
                    'images',
                    file_data,
                    filename=filename,
                    content_type='image/jpeg'
                )
                
                # Отправляем запрос
                url = f"{self.base_url}/classify_batch"
                
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"API error: {response.status} - {error_text}")
                        raise Exception(f"API error: {response.status}")
                        
        except asyncio.TimeoutError:
            logger.error("Request timeout")
            raise Exception("Превышено время ожидания ответа от сервера")
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise Exception("Ошибка сети при обращении к серверу")
        except Exception as e:
            logger.error(f"Unexpected error in classification service: {e}")
            raise
    
    async def classify_multiple_images(self, files: List[tuple]) -> Dict[str, Any]:
        """
        Классификация нескольких изображений
        
        Args:
            files: Список кортежей (file_data, filename)
            
        Returns:
            Результат классификации
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Подготавливаем данные для отправки
                data = aiohttp.FormData()
                
                for file_data, filename in files:
                    data.add_field(
                        'images',
                        file_data,
                        filename=filename,
                        content_type='image/jpeg'
                    )
                
                # Отправляем запрос
                url = f"{self.base_url}/classify_batch"
                
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"API error: {response.status} - {error_text}")
                        raise Exception(f"API error: {response.status}")
                        
        except asyncio.TimeoutError:
            logger.error("Request timeout")
            raise Exception("Превышено время ожидания ответа от сервера")
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise Exception("Ошибка сети при обращении к серверу")
        except Exception as e:
            logger.error(f"Unexpected error in classification service: {e}")
            raise
