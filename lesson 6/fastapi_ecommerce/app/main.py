from fastapi import FastAPI

from app.routers import categories, products, users, reviews


app = FastAPI(
    title="FastAPI shop",
    version="0.1.0",
)


app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)


@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to the shop"}