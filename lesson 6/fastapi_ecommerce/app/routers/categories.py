from fastapi import APIRouter


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/")
async def get_all_categories() -> dict:
    return {"message": "All categories (stub)"}


@router.post("/")
async def create_category() -> dict:
    return {"message": "Category was created (stub)"}


@router.put("/{category_id}")
async def update_category(category_id: int) -> dict:
    return {"message": f"Category with ID {category_id} was updated (stub)"}


@router.delete("/{category_id}")
async def delete_message(category_id: int) -> dict:
    return {"message": f"Message with ID {category_id} was deleted (stub)"}