from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File

from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.models.reviews import ReviewModel
from app.schemas import Product as ProductSchema, ProductCreate, Review as ReviewSchema, ProductList
from app.db_depends import get_async_db
from app.auth import get_current_seller

from datetime import date

from pathlib import Path
import uuid


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_ROOT = BASE_DIR / "media" / "products"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024 # 2 097 152 байт


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


async def save_product_image(file: UploadFile) -> str:
    """
    Сохраняет изображение товара и возвращает относительный URL.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only JPG, PNG or WebP images are allowed")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Image is too large")

    extension = Path(file.filename or "").suffix.lower() or ".jpg"
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = MEDIA_ROOT / file_name
    file_path.write_bytes(content)

    return f"/media/products/{file_name}"


def remove_product_image(url: str | None) -> None:
    """
    Удаляет файл изображения, если он существует.
    """
    if not url:
        return
    relative_path = url.lstrip("/")
    file_path = BASE_DIR / relative_path
    if file_path.exists():
        file_path.unlink()


@router.get("/", response_model=ProductList, status_code=status.HTTP_200_OK)
async def get_all_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = Query(None, description="ID категории для фильтрации"),
    search: str | None = Query(None, min_length=1, description="Поиск по названию товара"),
    min_price: float | None = Query(None, ge=0, description="Минимальная цена товара"),
    max_price: float | None = Query(None, ge=0, description="Максимальная цена товара"),
    in_stock: bool | None = Query(None, description="true — только товары в наличии, false — только без остатка"),
    max_created_date: date | None = Query(None, description="Максимальное время создания для фильтрации"),
    min_created_date: date | None = Query(None, description="Минимальное время создания для фильтрации"),
    seller_id: int | None = Query(None, description="ID продавца для фильтрации"),
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

    rank_col = None
    if search:
        search_value = search.strip()
        if search_value:
            ts_query = func.websearch_to_tsquery('english', search_value)
            filters.append(ProductModel.tsv.op('@@')(ts_query))
            rank_col = func.ts_rank_cd(ProductModel.tsv, ts_query).label("rank")
    
    total_products_count = (await db.scalar(
        select(func.count())
        .select_from(ProductModel)
        .where(*filters)
    )) or 0

    if rank_col is not None:
        products_stmt = (
            select(ProductModel, rank_col)
            .where(*filters)
            .order_by(desc(rank_col), ProductModel.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(products_stmt)
        rows = result.all()
        items = [row[0] for row in rows]    # сами объекты
    else:
        products_stmt = (
            select(ProductModel)
            .where(*filters)
            .order_by(ProductModel.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = (await db.scalars(products_stmt)).all()

    return {
        "items": items,
        "total": total_products_count,
        "page": page,
        "page_size": page_size,
    }


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate = Depends(ProductCreate.as_form),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
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
        
        image_url = await save_product_image(image) if image else None
    
        db_product = ProductModel(
            **product.model_dump(),
            seller_id=current_user.id,
            image_url=image_url,    
        )
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
    product: ProductCreate = Depends(ProductCreate.as_form),
    image: UploadFile | None = File(None),
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

        if image:
            remove_product_image(db_product.image_url)
            db_product.image_url = await save_product_image(image)

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
        
        remove_product_image(db_product.image_url)

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