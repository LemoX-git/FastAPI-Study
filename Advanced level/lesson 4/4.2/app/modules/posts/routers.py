from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_async_db
from app.modules.posts import crud
from app.modules.posts.schemas import Post, PostBase
from app.modules.categories import crud as categories_crud

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get("/", response_model=List[Post])
async def read_posts(category_id: int | None = None, skip: int = 0, limit: int = 100,
                     db: AsyncSession = Depends(get_async_db)):
    """Получить список всех постов или постов по ID категории."""
    if category_id is not None:
        # Проверяем, что категория существует (иначе вернём 404, а не пустой список)
        category = await categories_crud.get_category(db, category_id=category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")

    posts = await crud.get_posts(db, category_id=category_id, skip=skip, limit=limit)
    return posts


@router.post("/", response_model=Post, status_code=201)
async def create_post(post: PostBase, db: AsyncSession = Depends(get_async_db)):
    """Создать новый пост."""
    # Проверяем существование категории, используя CRUD из другого модуля
    category = await categories_crud.get_category(db, category_id=post.category_id)
    if category is None:
        raise HTTPException(status_code=400,
                            detail="Invalid category_id")

    # Создаем пост через CRUD своего модуля
    db_post = await crud.create_post(db=db, post=post)
    return db_post


@router.get("/{post_id}", response_model=Post)
async def read_post(post_id: int, db: AsyncSession = Depends(get_async_db)):
    """Получить пост по ID."""
    db_post = await crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post
