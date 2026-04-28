from fastapi import APIRouter


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/")
async def get_all_products() -> dict:
    return {"message": "All products (stub)"}


@router.post("/")
async def create_product() -> dict:
    return {"message": "Product was created (stub)"}


@router.get("/{product_id}")
async def get_product(product_id: int) -> dict:
    return {"message": f"Product {product_id} (stub)"}


@router.get("/category/{category_id}")
async def get_products_by_category(category_id: int) -> dict:
    return {"message": f"All products from {category_id} category (stub)"}


@router.put("/{product_id}")
async def update_product(product_id: int) -> dict:
    return {"message": f"Product {product_id} was updated"}


@router.delete("/{product_id}")
async def delete_product(product_id: int) -> dict:
    return {"message": f"Product {product_id} wqas deleted"}