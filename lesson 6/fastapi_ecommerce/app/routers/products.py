from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.models.reviews import ReviewModel
from app.schemas import Product as ProductSchema, ProductCreate, Review as ReviewSchema, ProductList
from app.db_depends import get_async_db
from app.auth import get_current_seller

from datetime import date


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=ProductList, status_code=status.HTTP_200_OK)
async def get_all_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = Query(
        None, description="ID категории для фильтрации"),
    min_price: float | None = Query(
        None, ge=0, description="Минимальная цена товара"),
    max_price: float | None = Query(
        None, ge=0, description="Максимальная цена товара"),
    in_stock: bool | None = Query(
        None, description="true — только товары в наличии, false — только без остатка"),
    max_created_date: date | None = Query(
        None, description="Максимальное время создания для фильтрации"
    ),
    min_created_date: date | None = Query(
        None, description="Минимальное время создания для фильтрации"
    ),
    seller_id: int | None = Query(
        None, description="ID продавца для фильтрации"),
    db: AsyncSession = Depends(get_async_db),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price не может быть больше max_price",
        )
    if min_created_date is not None and max_created_date is not None and min_created_date > max_created_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_created_date не может быть больше max_created_date",
        )
    
    # Формируем список фильтров
    filters = [ProductModel.is_active == True]

    if category_id is not None:
        filters.append(ProductModel.category_id == category_id)
    if min_price is not None:
        filters.append(ProductModel.price >= min_price)
    if max_price is not None:
        filters.append(ProductModel.price <= max_price)
    if in_stock is not None:
        filters.append(ProductModel.stock > 0 if in_stock else ProductModel.stock == 0)
    if seller_id is not None:
        filters.append(ProductModel.seller_id == seller_id)
    if max_created_date is not None:
        filters.append(ProductModel.created_at <= max_created_date)
    if min_created_date is not None:
        filters.append(ProductModel.created_at >= min_created_date)
    
    total_products_count = (await db.scalar(
        select(func.count(ProductModel.id))
        .where(*filters)
    )) or 0

    items = (await db.scalars(
        select(ProductModel)
        .where(*filters)
        .order_by(ProductModel.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).all()

    return {
        "items": items,
        "total": total_products_count,
        "page": page,
        "page_size": page_size,
    }


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