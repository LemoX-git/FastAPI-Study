from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import categories, posts


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается. Создаем базу данных...")
    await create_db_and_tables()
    print("База данных инициализирована.")
    yield
    print("Приложение завершает работу.")


app = FastAPI(
    title="Простой Блог на FastAPI с SQLAlchemy 2.0",
    lifespan=lifespan
)

app.include_router(categories.router)
app.include_router(posts.router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Это проект из курса 'Продвинутый FastAPI для продолжающих'"}
