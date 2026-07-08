from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI()


@app.get("/welcome", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    return "<h1>Welcome to FastAPI</h1>"