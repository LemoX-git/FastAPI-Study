from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


app = FastAPI()


@app.get("/status", response_class=PlainTextResponse, status_code=200)
async def root() -> PlainTextResponse:
    return "API is running"