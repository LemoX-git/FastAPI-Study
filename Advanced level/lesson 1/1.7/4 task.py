from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse


app = FastAPI()


@app.get("/home", response_class=JSONResponse)
async def home() -> JSONResponse:
    return JSONResponse(
        content={"page": "Home"},
    )


@app.get("/go-home", response_class=RedirectResponse)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/home", status_code=302)