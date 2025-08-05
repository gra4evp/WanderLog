# services/backend/main.py
import asyncio
import logging
import os
from contextlib import asynccontextmanager

from db.database import create_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import location_router, user_router
from sqlalchemy.exc import OperationalError, SQLAlchemyError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(f"uvicorn.{__name__}")

MAX_DB_CONNECTION_RETRIES = int(os.getenv("MAX_DB_CONNECTION_RETRIES", 5))
RETRY_DB_CONNECTION_DELAY = int(os.getenv("RETRY_DB_CONNECTION_DELAY", 5))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles database table creation with retry logic on startup.
    """
    logger.info("Starting table creation process")

    retries = 0
    # Retry loop for database connection with exponential backoff
    while retries < MAX_DB_CONNECTION_RETRIES:
        try:
            await create_tables()
            break  # Success - exit retry loop
        except (OperationalError, SQLAlchemyError) as e:
            retries += 1
            logger.error(f"Database connection error (attempt {retries}/{MAX_DB_CONNECTION_RETRIES}): {e}")

            # Check if we should retry or give up
            if retries < MAX_DB_CONNECTION_RETRIES:
                logger.info(f"Retrying in {RETRY_DB_CONNECTION_DELAY} seconds...")
                await asyncio.sleep(RETRY_DB_CONNECTION_DELAY)
            else:
                logger.error("Maximum number of connection attempts exceeded.")
                raise  # Re-raise exception if retries are exhausted
        except Exception as e:
            # Handle unexpected errors - don't retry for these
            logger.error(f"Unexpected database error: {e}")
            raise  # Re-raise exception for other errors

    logger.info("Tables created successfully")
    yield  # Application startup complete, yield control to FastAPI


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Создаем FastAPI приложение
app = FastAPI(
    title="WanderLog API",
    description="API for WanderLog",
    version="1.0.0",
    lifespan=lifespan,
    prefix="/api",
    openapi_url="/openapi.json",  # URL для получения OpenAPI схемы
    docs_url="/docs",  # URL для Swagger UI
    redoc_url="/redoc",  # URL для ReDoc
    swagger_ui_parameters={
        "persistAuthorization": True,  # Сохранять токен авторизации между запросами
        "displayRequestDuration": True,  # Показывать время выполнения запросов
        "filter": True,  # Включать фильтрацию эндпоинтов
        "deepLinking": True,  # Включать глубокие ссылки на эндпоинты
        "displayOperationId": False,  # Показывать ID операций
        "defaultModelsExpandDepth": -1,  # Глубина раскрытия моделей по умолчанию (-1 = все)
        "defaultModelExpandDepth": 1,  # Глубина раскрытия одной модели
        "defaultModelRendering": "model",  # Способ отображения моделей
        "docExpansion": "list",  # Начальное состояние документации (none/list/full)
        "showExtensions": True,  # Показывать расширения OpenAPI
        "showCommonExtensions": True,  # Показывать общие расширения
        "supportedSubmitMethods": [  # Поддерживаемые HTTP методы
            "get", "post", "put", "delete", "options", "head", "patch", "trace"
        ],
        "tryItOutEnabled": True,  # Включать кнопку "Try it out"
        "syntaxHighlight": {  # Настройки подсветки синтаксиса
            "activated": True,
            "theme": "monokai"  # Тема подсветки
        }
    }
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(location_router)
app.include_router(user_router)

# Запуск сервер
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8015))  # Берём порт из переменной или 8000 по умолчанию
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
