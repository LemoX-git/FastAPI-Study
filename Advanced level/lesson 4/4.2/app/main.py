from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.modules.categories import routers as categories_routers
from app.modules.posts import routers as posts_routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается. Создаем базу данных...")
    await create_db_and_tables()
    print("База данных инициализирована.")
    yield
    print("Приложение завершает работу.")


app = FastAPI(
    title="Простой Блог на FastAPI с SQLAlchemy",
    lifespan=lifespan
)

app.include_router(categories_routers.router)
app.include_router(posts_routers.router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Это проект из курса 'Продвинутый FastAPI для продолжающих'"}
