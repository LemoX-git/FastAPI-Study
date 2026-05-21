from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_db


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)):
    query = select(ProductModel).where(ProductModel.is_active == True)
    return db.scalars(query).all()


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    if product.category_id is not None:
        category_exists = db.scalar(select(CategoryModel.id).where(
                CategoryModel.id == product.category_id,
                CategoryModel.is_active == True,
            )
        )
        if category_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Category not found or inactive"
                                )
    
        db_product = ProductModel(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    if product_id is not None:
        db_product = db.scalars(select(ProductModel).where(ProductModel.id == product_id)).first()
        if db_product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
        return db_product
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="product_id must not be null"
                        )


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    if category_id is not None:
        category_exists = db.scalar(select(CategoryModel.id).where(
                CategoryModel.id == category_id,
                CategoryModel.is_active == True,
            )
        )
        if category_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Category not found or inactive"
                                )
    
        products = db.scalars(select(ProductModel).where(
                ProductModel.category_id == category_id,
                ProductModel.is_active == True,
            )
        ).all()
        return products
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="category_id must not be null"
                        )


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    if product_id is not None:
        db_product = db.scalars(select(ProductModel).where(ProductModel.id == product_id)).first()
        if db_product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
        category_exists = db.scalar(select(CategoryModel.id).where(
                    CategoryModel.id == product.category_id,
                    CategoryModel.is_active == True,
                )
            )
        if category_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="category_id not found or inactive"
                                )
        
        db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**product.model_dump())
        )
        db.commit()
        db.refresh(db_product)
        return db_product
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="product_id must not be null"
                        )


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    if product_id is not None:
        db_product = db.scalar(select(ProductModel).where(
                ProductModel.id == product_id,
                ProductModel.is_active == True,
            )
        )
        if db_product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="product not found or inactive")
        
        db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(is_active = False)
        )
        db.commit()
        return {"status": "succes", "message": "Product marked as inactive"}
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="product_id must not be null"
                        )