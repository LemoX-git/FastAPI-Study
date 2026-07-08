from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI()


@app.get("/user/{name}", response_class=HTMLResponse)
async def root(name: str) -> HTMLResponse:
    return HTMLResponse(
        content=f"<h1>Hello, {name}!</h1>"
    )