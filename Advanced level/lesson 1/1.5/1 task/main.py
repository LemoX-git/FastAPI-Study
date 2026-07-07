from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting...")

    yield

    print("Application is shutting down...")


app = FastAPI(lifespan=lifespan)