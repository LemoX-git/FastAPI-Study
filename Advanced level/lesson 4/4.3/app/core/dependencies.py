from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.repositories.categories import CategoryRepository
from app.repositories.posts import PostRepository
from app.services.categories import CategoryService
from app.services.posts import PostService


async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db


# Зависимости для получения экземпляров репозиториев
def get_category_repository(db: AsyncSession = Depends(get_async_db)) -> CategoryRepository:
    return CategoryRepository(db=db)


def get_post_repository(db: AsyncSession = Depends(get_async_db)) -> PostRepository:
    return PostRepository(db=db)


# Зависимости для получения экземпляров сервисов
def get_category_service(repo: CategoryRepository = Depends(get_category_repository)) -> CategoryService:
    return CategoryService(category_repo=repo)


def get_post_service(
    post_repo: PostRepository = Depends(get_post_repository),
    category_repo: CategoryRepository = Depends(get_category_repository),
) -> PostService:
    return PostService(
        post_repo=post_repo,
        category_repo=category_repo,  # Посту нужен доступ к категориям для валидации
    )
