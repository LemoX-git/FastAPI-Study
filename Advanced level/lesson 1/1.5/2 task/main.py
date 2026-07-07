from fastapi import FastAPI
from contextlib import asynccontextmanager
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        start = time.time_ns()

        yield

    except Exception as e:
        print(f"Error: {e}")

    finally:
        end = time.time_ns()

        result = end - start

        second_of_minute = time.localtime(result // 1_000_000_000).tm_sec
        microseconds = (result % 1_000_000_000) // 1_000

        microseconds_2 = microseconds // 10_000

        print(f"Application ran for {second_of_minute}.{microseconds_2:02d} seconds")


app = FastAPI(lifespan=lifespan)
