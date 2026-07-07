from fastapi import FastAPI, Request
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.request_count = 0
        print("Request counter initialized")
        yield

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print(f"Total requests: {app.state.request_count}")
        app.state.request_count = 0


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root(request: Request) -> dict:
    request.app.state.request_count += 1
    return {
        "message": "Hello, World!"
    }