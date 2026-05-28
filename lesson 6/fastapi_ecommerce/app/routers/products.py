from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.models.reviews import ReviewModel
from app.schemas import Product as ProductSchema, ProductCreate, Review as ReviewSchema
from app.db_depends import get_async_db
from app.auth import get_current_seller


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    query = select(ProductModel).where(ProductModel.is_active == True)
    return (await db.scalars(query)).all()


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    if product.category_id is not None:
        category_exists = await db.scalar(select(CategoryModel.id).where(
                CategoryModel.id == product.category_id,
                CategoryModel.is_active == True,
            )
        )
        if category_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Category not found or inactive"
                                )
    
        db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    if product_id is not None:
        db_product = (await db.scalars(select(ProductModel).where(ProductModel.id == product_id))).first()
        if db_product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
        return db_product
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="product_id must not be null"
                        )


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    if category_id is not None:
        category_exists = await db.scalar(select(CategoryModel.id).where(
                CategoryModel.id == category_id,
                CategoryModel.is_active == True,
            )
        )
        if category_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Category not found or inactive"
                                )
    
        products = (await db.scalars(select(ProductModel).where(
                ProductModel.category_id == category_id,
                ProductModel.is_active == True,
            )
        )).all()
        return products
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="category_id must not be null"
                        )


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int, 
    product: ProductCreate, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    if product_id is not None:
        db_product = (await db.scalars(select(ProductModel).where(ProductModel.id == product_id))).first()
        if db_product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
        category_exists = await db.scalar(select(CategoryModel.id).where(
                    CategoryModel.id == product.category_id,
                    CategoryModel.is_active == True,
                )
            )
        if category_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="category_id not found or inactive"
                                )
        
        if current_user.id != db_product.seller_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
        
        await db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**product.model_dump())
        )
        await db.commit()
        await db.refresh(db_product)
        return db_product
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="product_id must not be null"
                        )


@router.delete("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    if product_id is not None:
        db_product = await db.scalar(select(ProductModel).where(
                ProductModel.id == product_id,
                ProductModel.is_active == True,
            )
        )
        if db_product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="product not found or inactive")
        
        if current_user.id != db_product.seller_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You can only update your own products")
        
        await db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(is_active = False)
        )
        await db.commit()
        await db.refresh(db_product)
        
        return db_product
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="product_id must not be null"
                        )


@router.get("/{product_id}/reviews", response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_product_reviews(
    product_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    product = (await db.scalars(
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .where(ProductModel.is_active == True)
    )).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    reviews = (await db.scalars(
        select(ReviewModel)
        .where(ReviewModel.product_id == product.id)
        .where(ReviewModel.is_active == True)
    )).all()
    return reviews