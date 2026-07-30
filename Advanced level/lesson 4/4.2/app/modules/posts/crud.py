from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.posts.models import Post
from app.modules.posts.schemas import PostBase


# Получить пост по ID
async def get_post(db: AsyncSession, post_id: int):
    result = await db.scalars(select(Post).filter(Post.id == post_id))
    return result.first()


# Получить список всех постов или по ID категории
async def get_posts(db: AsyncSession, category_id: int | None = None, skip: int = 0, limit: int = 100):
    query = select(Post)
    if category_id is not None:
        query = query.filter(Post.category_id == category_id)
    result = await db.scalars(query.offset(skip).limit(limit))
    return result.all()


# Создать новый пост
async def create_post(db: AsyncSession, post: PostBase):
    # Проверяем существование категории, используя CRUD из другого модуля
    db_post = Post(
        title=post.title,
        content=post.content,
        category_id=post.category_id
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post
