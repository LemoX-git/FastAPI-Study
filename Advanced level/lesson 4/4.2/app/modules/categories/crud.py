from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.categories.models import Category
from app.modules.categories.schemas import CategoryBase


# Получить категорию по ID
async def get_category(db: AsyncSession, category_id: int):
    result = await db.scalar(select(Category).filter(Category.id == category_id))
    return result


# Получить категорию по имени
async def get_category_by_name(db: AsyncSession, name: str):
    result = await db.scalars(select(Category).filter(Category.name == name))
    return result.first()


# Получить список всех категорий
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.scalars(select(Category).offset(skip).limit(limit))
    return result.all()


# Создать новую категорию
async def create_category(db: AsyncSession, category: CategoryBase):
    db_category = Category(name=category.name)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category