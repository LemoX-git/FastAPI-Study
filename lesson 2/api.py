from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def welcome() -> dict:
    return {"message": "Hello, World!"}


@app.get("/user")
async def login(username: str, age: int) -> dict:
    return {"user": username, "age": age}


@app.get("/hello/{user}")
async def welcome_user(user: str) -> dict:
    return {"user": f"Hello, {user}"}


@app.get("/hello/{first_name}/{last_name}")
async def welcome_user_fullname(first_name: str, last_name: str) -> dict:
    return {"user": f"Hello, {first_name} {last_name}"}


@app.get("/order/{order_id}")
async def order(order_id: int) -> dict:
    return {"id": order_id}


@app.get("/products/{product_id}")
async def products(product_id : int) -> dict:
    return {"product": f"Stock number {product_id}"}