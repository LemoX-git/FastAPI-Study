from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn


# Глобальные переменные для хранения ресурсов
db_connection_pool = None
ml_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код ДО yield: Выполняется при СТАРТЕ приложения
    print("Приложение запускается: Инициализация ресурсов...")
    global db_connection_pool
    global ml_model

    try:
        # Инициализация пула соединений с базой данных
        db_connection_pool = {"status": "connected", "connections": 10}
        print(f"Пул БД инициализирован: {db_connection_pool}")

        # Загрузка большой модели машинного обучения
        ml_model = {"name": "SentimentAnalysisModel", "version": "1.0"}
        print(f"Модель ML загружена: {ml_model}")

        # Здесь можно запустить фоновые задачи, инициализировать кэши и т.д.
        print("Ресурсы успешно инициализированы.")

        # yield - это разделитель!
        # Код после yield будет выполнен только при остановке приложения.
        yield

    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        # В случае ошибки при запуске, приложение не будет запущено
        raise # Перевыбрасываем исключение, чтобы сервер не стартовал

    finally:
        # Код ПОСЛЕ yield (или в finally блока): Выполняется при ОСТАНОВКЕ приложения
        print("Приложение останавливается: Очистка ресурсов...")
        if db_connection_pool:
            # Закрытие пула соединений с БД
            db_connection_pool = None
            print("Пул БД закрыт.")
        if ml_model:
            # Выгрузка модели ML
            ml_model = None
            print("Модель ML выгружена.")
        print("Ресурсы успешно очищены. Приложение остановлено.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    # Теперь мы можем использовать глобальные ресурсы
    if db_connection_pool and ml_model:
        return {
            "message": "Hello from FastAPI!",
            "db_status": db_connection_pool["status"],
            "model_name": ml_model["name"]
        }
    return {"message": "Resources not available!"}
