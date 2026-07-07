from fastapi import FastAPI
from contextlib import asynccontextmanager
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with open("temp.txt", "w", encoding="utf-8") as file:
            file.write("Hello, FastAPI!")

        print("Temporary file created")

        yield

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if os.path.exists("temp.txt"):
            os.remove("temp.txt")

        print("Temporary file deleted")


app = FastAPI(lifespan=lifespan)
