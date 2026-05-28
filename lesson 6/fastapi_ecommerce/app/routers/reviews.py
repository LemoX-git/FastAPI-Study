from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import ReviewModel 
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas import Review as ReviewSchemas, ReviewCreate
from app.db_depends import get_async_db
from app.auth import get_current_buyer, get_current_user


router = APIRouter(prefix="/reviews", tags=["reviews"])


async def update_product_rating(
    db: AsyncSession,
    product_id: int,
    auto_commit: bool = False
):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    
    if auto_commit:
        await db.commit()


@router.get("/", response_model=list[ReviewSchemas], status_code=status.HTTP_200_OK)
async def get_reviews(
    db: AsyncSession = Depends(get_async_db)
):
    reviews = (await db.scalars(
        select(ReviewModel)
        .where(ReviewModel.is_active == True)
    )).all()
    return reviews


@router.post("/", response_model=ReviewSchemas, status_code=status.HTTP_201_CREATED)
async def create_review(
    new_review: ReviewCreate,
    current_user: UserModel = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_async_db)
):
    product = (await db.scalars(
        select(ProductModel)
        .where(ProductModel.id == new_review.product_id)
        .where(ProductModel.is_active == True)
    )).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    user = (await db.scalars(
        select(UserModel)
        .where(UserModel.id == current_user.id)
        .where(UserModel.is_active == True)
    )).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only user with role 'buyer' can leave feedback"
        )
    
    new_review_db = ReviewModel(**new_review.model_dump())
    new_review_db.user_id = current_user.id
    db.add(new_review_db)
    await db.flush()

    await update_product_rating(db=db, product_id=product.id)

    await db.commit()
    await db.refresh(new_review_db)

    return new_review_db


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    current_user: UserModel = Depends(get_current_user), # Используется именно get_current_user, потому что иначе никакой admin не пройдет на этапе зависимостей.
                                                         # Либо же надо добавлять новую роль в БД. Или надо еще какую логику городить.
    db: AsyncSession = Depends(get_async_db) 
):
    review = (await db.scalars(
        select(ReviewModel)
        .where(ReviewModel.id == review_id)
        .where(ReviewModel.is_active == True)
    )).first()
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or inactive"
        )
    
    if current_user.role != "admin" and current_user.id != review.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can delete review"
        )
    
    product = (await db.scalars(
        select(ProductModel)
        .where(ProductModel.id == review.product_id)
        .where(ProductModel.is_active == True) 
    )).first()
    # Данная логика предполагает невозможность удалять отзывы для неактивных продуктов
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )
    
    review.is_active = False
    await db.flush()

    await update_product_rating(db=db, product_id=product.id)

    await db.commit()

    return {"message": "Review deleted"}