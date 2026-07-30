from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_async_db
from app.modules.categories import crud
from app.modules.categories.schemas import Category, CategoryBase

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("/", response_model=List[Category])
async def read_categories(skip: int = 0, limit: int = 100,
                          db: AsyncSession = Depends(get_async_db)):
    """Получить список всех категорий."""
    return await crud.get_categories(db, skip=skip, limit=limit)


@router.post("/", response_model=Category, status_code=201)
async def create_category(category: CategoryBase, db: AsyncSession = Depends(get_async_db)):
    """Создать новую категорию."""
    db_category = await crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    return await crud.create_category(db=db, category=category)


@router.get("/{category_id}", response_model=Category)
async def read_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """Получить категорию по ID."""
    db_category = await crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category