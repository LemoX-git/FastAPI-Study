from fastapi import FastAPI, APIRouter, HTTPException, status


app = FastAPI(title="Nested Users API")

# фейковые данные
_users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]

@app.get("/")
async def root() -> None:
    pass

root_router = APIRouter()

@root_router.get("/")
async def show_hellow_message() -> dict:
    return {"messgae": "Hellow, World!"}

users_router = APIRouter(prefix="/users")

@users_router.get("/")
async def get_users() -> list[dict]:
    return _users

@users_router.get("/{user_id}")
async def get_user_by_id(user_id: int) -> dict:
    for user in _users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

root_router.include_router(users_router)

app.include_router(root_router, prefix="/api")