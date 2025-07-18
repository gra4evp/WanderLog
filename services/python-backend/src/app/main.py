# services/backend/main.py
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.classify import router as classify_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(f"uvicorn.{__name__}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


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
    title="Image Classification API",
    description="API for classifying apartment images",
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

app.include_router(classify_router)

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
